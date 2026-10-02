// A port of CPython's `random` module (Mersenne Twister MT19937) covering the
// calls the simulator makes. Matching CPython exactly keeps seeds shareable
// between the desktop (Python) and web versions: the same seed string produces
// the same boards, columns and spice traps in both.
import { sha512 } from '@noble/hashes/sha2.js';

const N = 624;
const M = 397;

export class PyRandom {
  private mt = new Uint32Array(N);
  private mti = N + 1;

  constructor(seed?: string) {
    if (seed === undefined) this.seedFromCrypto();
    else this.seed(seed);
  }

  /** Equivalent to Python's `random.seed(some_str)` (version 2 seeding). */
  seed(a: string): void {
    const encoded = new TextEncoder().encode(a);
    const digest = sha512(encoded);
    // int.from_bytes(a.encode() + sha512(a.encode()).digest()) is big-endian.
    const bytes = new Uint8Array(encoded.length + digest.length);
    bytes.set(encoded, 0);
    bytes.set(digest, encoded.length);
    this.initByArray(bigEndianBytesToKey(bytes));
  }

  seedFromCrypto(): void {
    const key = new Uint32Array(N);
    crypto.getRandomValues(key);
    this.initByArray(Array.from(key));
  }

  private initGenrand(s: number): void {
    const mt = this.mt;
    mt[0] = s >>> 0;
    for (let i = 1; i < N; i++) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (Math.imul(1812433253, prev) + i) >>> 0;
    }
    this.mti = N;
  }

  private initByArray(key: number[]): void {
    const mt = this.mt;
    this.initGenrand(19650218);
    let i = 1;
    let j = 0;
    const keyLength = key.length;
    for (let k = Math.max(N, keyLength); k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(prev, 1664525)) + key[j] + j) >>> 0;
      i++;
      j++;
      if (i >= N) {
        mt[0] = mt[N - 1];
        i = 1;
      }
      if (j >= keyLength) j = 0;
    }
    for (let k = N - 1; k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(prev, 1566083941)) - i) >>> 0;
      i++;
      if (i >= N) {
        mt[0] = mt[N - 1];
        i = 1;
      }
    }
    mt[0] = 0x80000000;
    this.mti = N;
  }

  private genrandUint32(): number {
    const mt = this.mt;
    let y: number;
    if (this.mti >= N) {
      let kk = 0;
      for (; kk < N - M; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + M] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      for (; kk < N - 1; kk++) {
        y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
        mt[kk] = mt[kk + (M - N)] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      y = (mt[N - 1] & 0x80000000) | (mt[0] & 0x7fffffff);
      mt[N - 1] = mt[M - 1] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      this.mti = 0;
    }
    y = mt[this.mti++];
    y ^= y >>> 11;
    y ^= (y << 7) & 0x9d2c5680;
    y ^= (y << 15) & 0xefc60000;
    y ^= y >>> 18;
    return y >>> 0;
  }

  /** random.random() */
  random(): number {
    const a = this.genrandUint32() >>> 5;
    const b = this.genrandUint32() >>> 6;
    return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
  }

  /** random.getrandbits(k) */
  getrandbits(k: number): bigint {
    if (k <= 32) return BigInt(this.genrandUint32() >>> (32 - k));
    let result = 0n;
    let shift = 0n;
    for (let remaining = k; remaining > 0; remaining -= 32) {
      let r = this.genrandUint32();
      if (remaining < 32) r >>>= 32 - remaining;
      result |= BigInt(r) << shift;
      shift += 32n;
    }
    return result;
  }

  /** Random._randbelow_with_getrandbits */
  randbelow(n: bigint): bigint {
    const k = n.toString(2).length;
    let r = this.getrandbits(k);
    while (r >= n) r = this.getrandbits(k);
    return r;
  }

  /** random.randint(a, b) */
  randint(a: bigint, b: bigint): bigint {
    return a + this.randbelow(b - a + 1n);
  }

  /** random.choice(seq) */
  choice<T>(seq: readonly T[]): T {
    return seq[Number(this.randbelow(BigInt(seq.length)))];
  }

  /** random.choices(population, weights, k=1)[0] */
  choiceWeighted<T>(population: readonly T[], weights: readonly number[]): T {
    const cumWeights: number[] = [];
    let total = 0;
    for (const w of weights) {
      total += w;
      cumWeights.push(total);
    }
    // Python raises ValueError here; the web version picks the last option
    // rather than freezing the game loop.
    if (!(total > 0)) return population[population.length - 1];
    const hi = population.length - 1;
    return population[bisectRight(cumWeights, this.random() * total, 0, hi)];
  }
}

function bisectRight(a: number[], x: number, lo: number, hi: number): number {
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (x < a[mid]) hi = mid;
    else lo = mid + 1;
  }
  return lo;
}

/** Converts a big-endian unsigned integer into the little-endian 32-bit words CPython feeds init_by_array. */
function bigEndianBytesToKey(bytes: Uint8Array): number[] {
  let start = 0;
  while (start < bytes.length && bytes[start] === 0) start++;
  const significant = bytes.subarray(start);
  if (significant.length === 0) return [0];
  const key: number[] = [];
  for (let end = significant.length; end > 0; end -= 4) {
    let word = 0;
    for (let b = Math.max(0, end - 4); b < end; b++) word = (word * 256 + significant[b]) >>> 0;
    key.push(word);
  }
  return key;
}
