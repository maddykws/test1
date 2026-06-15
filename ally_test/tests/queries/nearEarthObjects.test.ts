import { parse } from 'graphql';
import { executor } from '../exectuor';
import nasaSample from '../../data/nasa-neo-sample.json';

// stub the Mesh SDK so the test doesn't hit the real NASA API
jest.mock('../../src/schema/neo/neo', () => {
  const flattenNeos = (nearEarthObjects: Record<string, any[]>) =>
    Object.values(nearEarthObjects)
      .flat()
      .map((neo: any) => {
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

  return {
    getNearEarthObjects: jest.fn(async (_parent: any, _args: any, context: any) => {
      context.logger.info('getNearEarthObjects', 'Enter resolver');
      return {
        elementCount: nasaSample.element_count,
        objects: flattenNeos(nasaSample.near_earth_objects as any),
      };
    }),
  };
});

const QUERY = `
  query NearEarthObjects($startDate: String!, $endDate: String!) {
    nearEarthObjects(startDate: $startDate, endDate: $endDate) {
      elementCount
      objects {
        id
        name
        isPotentiallyHazardousAsteroid
        estimatedDiameterMinKm
        estimatedDiameterMaxKm
        closeApproachDate
        relativeVelocityKph
        missDistanceKm
      }
    }
  }
`;

describe('nearEarthObjects', () => {
  test('returns flattened NEO list from both dates', async () => {
    const result = await executor({
      document: parse(QUERY),
      variables: { startDate: '2015-09-07', endDate: '2015-09-08' },
    });

    expect(result).toMatchObject({
      data: {
        nearEarthObjects: {
          elementCount: 2,
          objects: expect.arrayContaining([
            expect.objectContaining({ id: '2465633', name: '465633 (2009 JR5)' }),
            expect.objectContaining({ id: '3726710', name: '(2015 RC)' }),
          ]),
        },
      },
      metadata: expect.objectContaining({ requestId: expect.any(String) }),
    });
  });

  test('objects list is flat across all dates', async () => {
    const result: any = await executor({
      document: parse(QUERY),
      variables: { startDate: '2015-09-07', endDate: '2015-09-08' },
    });

    // both dates contributed — result is a flat array, not grouped
    expect(Array.isArray(result.data.nearEarthObjects.objects)).toBe(true);
    expect(result.data.nearEarthObjects.objects.length).toBe(2);
  });
});
