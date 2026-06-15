import { getMesh } from '@graphql-mesh/runtime';
import { findAndParseConfig } from '@graphql-mesh/cli';
import path from 'path';

// Mesh SDK is initialised once and shared across requests
let meshSdkPromise: Promise<any> | null = null;

const getMeshSdk = () => {
  if (!meshSdkPromise) {
    meshSdkPromise = findAndParseConfig({
      dir: path.join(__dirname, '../../../'),
    }).then((config: any) => getMesh(config));
  }
  return meshSdkPromise;
};

type RawNeo = {
  id: string;
  name: string;
  is_potentially_hazardous_asteroid: boolean;
  estimated_diameter: {
    kilometers: {
      estimated_diameter_min: number;
      estimated_diameter_max: number;
    };
  };
  close_approach_data: Array<{
    close_approach_date: string;
    relative_velocity: { kilometers_per_hour: string };
    miss_distance: { kilometers: string };
  }>;
};

// flatten the date-keyed map into a single list and pick only the fields we expose
const flattenNeos = (nearEarthObjects: Record<string, RawNeo[]>) => {
  return Object.values(nearEarthObjects)
    .flat()
    .map((neo) => {
      const approach = neo.close_approach_data?.[0];
      return {
        id: neo.id,
        name: neo.name,
        isPotentiallyHazardousAsteroid: neo.is_potentially_hazardous_asteroid,
        estimatedDiameterMinKm: neo.estimated_diameter?.kilometers?.estimated_diameter_min,
        estimatedDiameterMaxKm: neo.estimated_diameter?.kilometers?.estimated_diameter_max,
        closeApproachDate: approach?.close_approach_date,
        relativeVelocityKph: approach?.relative_velocity?.kilometers_per_hour,
        missDistanceKm: approach?.miss_distance?.kilometers,
      };
    });
};

export const getNearEarthObjects = async (
  _: any,
  args: { startDate: string; endDate: string },
  context: any
) => {
  context.logger.info('getNearEarthObjects', 'Enter resolver');
  const { sdk } = await getMeshSdk();
  const raw = await sdk.nasaNeoFeed({ startDate: args.startDate, endDate: args.endDate });

  return {
    elementCount: raw.element_count,
    objects: flattenNeos(raw.near_earth_objects ?? {}),
  };
};
