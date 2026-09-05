const CRITERIA_KEYS = [
  "attributable",
  "legible",
  "contemporaneous",
  "original",
  "accurate",
  "complete",
  "consistent",
  "enduring",
  "available",
];

const RATING_WEIGHTS = { compliant: 1, minor: 0.5, major: 0, na: null };

function computeScore(criteria) {
  let total = 0, count = 0;
  for (const key of CRITERIA_KEYS) {
    const rating = criteria[key] && criteria[key].rating;
    const weight = RATING_WEIGHTS[rating];
    if (weight !== null && weight !== undefined) {
      total += weight;
      count += 1;
    }
  }
  if (count === 0) return null;
  return Math.round((total / count) * 100);
}

function statusFromScore(score) {
  if (score === null) return "attention";
  if (score >= 90) return "compliant";
  if (score >= 70) return "attention";
  return "noncompliant";
}

module.exports = { CRITERIA_KEYS, computeScore, statusFromScore };
