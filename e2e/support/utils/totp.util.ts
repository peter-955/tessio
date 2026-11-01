import { createHmac } from "node:crypto";

const BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
const TIME_STEP_SECONDS = 30;
const CODE_DIGITS = 6;
const BITS_PER_BASE32_CHARACTER = 5;
const BITS_PER_BYTE = 8;

const decodeBase32 = (base32Key: string): Buffer => {
  const characters = base32Key.toUpperCase().replace(/[\s=]/g, "");
  const bytes: number[] = [];
  let buffer = 0;
  let bufferedBits = 0;
  for (const character of characters) {
    const value = BASE32_ALPHABET.indexOf(character);
    if (value === -1) {
      throw new Error(`Invalid base32 character: ${character}`);
    }
    buffer = (buffer << BITS_PER_BASE32_CHARACTER) | value;
    bufferedBits += BITS_PER_BASE32_CHARACTER;
    if (bufferedBits >= BITS_PER_BYTE) {
      bufferedBits -= BITS_PER_BYTE;
      bytes.push((buffer >> bufferedBits) & 0xff);
    }
  }
  return Buffer.from(bytes);
};

export const generateTotpCode = (
  base32Key: string,
  timestampMilliseconds: number = Date.now(),
): string => {
  const counter = Math.floor(timestampMilliseconds / 1000 / TIME_STEP_SECONDS);
  const counterBytes = Buffer.alloc(8);
  counterBytes.writeBigUInt64BE(BigInt(counter));
  const digest = createHmac("sha1", decodeBase32(base32Key)).update(counterBytes).digest();
  const offset = (digest[digest.length - 1] ?? 0) & 0x0f;
  const binary = digest.readUInt32BE(offset) & 0x7fffffff;
  return String(binary % 10 ** CODE_DIGITS).padStart(CODE_DIGITS, "0");
};
