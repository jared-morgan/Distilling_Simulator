import { describe, expect, it } from 'vitest';
import { PyRandom } from '../src/pyrandom';

// Expected values were produced by CPython 3.11 with the same calls.
describe('PyRandom matches CPython', () => {
  it('reproduces a seeded sequence', () => {
    const r = new PyRandom('12345678901234567890');
    expect([r.random(), r.random(), r.random()]).toEqual([0.8967849279005352, 0.7135791664360509, 0.0014732709980934677]);
    const picks = Array.from({ length: 5 }, () => r.choiceWeighted([0, 1, 2, 3, 4], [10, 10, 0, 1, 10]));
    expect(picks).toEqual([0, 1, 4, 4, 4]);
    expect(Array.from({ length: 6 }, () => r.choice([true, false]))).toEqual([true, false, true, false, true, false]);
    expect(r.choice([1, 2, 3, 4, 5])).toBe(3);
    expect(r.getrandbits(67)).toBe(64873297546205800181n);
    expect(r.randint(10n ** 19n, 10n ** 20n - 1n)).toBe(31289452504423553806n);
  });

  it('seeds from an empty string', () => {
    expect(new PyRandom('').random()).toBe(0.9602256525641875);
  });
});
