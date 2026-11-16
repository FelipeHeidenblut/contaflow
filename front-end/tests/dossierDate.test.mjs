import assert from 'node:assert/strict'
import test from 'node:test'
import { formatDossierDate } from '../src/utils/dossierDate.ts'

test('document timestamps use the date in São Paulo, including UTC midnight boundaries', () => {
  assert.equal(formatDossierDate('2026-11-16T16:38:50.757773Z'), '16/11/2026')
  assert.equal(formatDossierDate('2026-11-16T01:00:00Z'), '15/11/2026')
  assert.equal(formatDossierDate('2026-11-16T01:00:00-03:00'), '16/11/2026')
})

test('task deadlines stay on their calendar date', () => {
  assert.equal(formatDossierDate('2026-11-16'), '16/11/2026')
  assert.equal(formatDossierDate('2028-02-29'), '29/02/2028')
})

test('missing, invalid or ambiguous dates have a safe fallback', () => {
  for (const value of [
    null,
    undefined,
    '',
    'invalid',
    '2026-02-30',
    '2026-02-30T12:00:00Z',
    '2026-11-16T01:00:00',
  ]) {
    assert.equal(formatDossierDate(value), '-')
  }
})
