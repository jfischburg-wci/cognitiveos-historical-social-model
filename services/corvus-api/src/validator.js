import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';

// Resolve schema path relative to repo root so it works from src/ and dist/
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.resolve(__dirname, '../../../packages/schema/corvid_directives.schema.json');

let schema;
try {
  const raw = fs.readFileSync(schemaPath, 'utf-8');
  schema = JSON.parse(raw);
} catch (err) {
  console.error('Failed to read schema at', schemaPath, err);
  schema = null;
}

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);

const validate = schema ? ajv.compile(schema) : null;

export function validateDirectives(payload) {
  if (!validate) {
    return { valid: false, errors: [{ message: 'Schema not loaded' }] };
  }
  const ok = validate(payload);
  if (!ok) {
    return { valid: false, errors: validate.errors };
  }
  return { valid: true };
}
