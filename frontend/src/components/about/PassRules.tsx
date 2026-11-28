export default function PassRules() {
  return (
    <p className="about-note">
      <b>PASS</b>: the measured success rate is at least 50% of the ideal success rate, with no help
      (75% for Simon's, because random guessing already scores 50%). <b>RECOVERED</b>: it failed at
      first, but passed after ZNE. <b>FAIL</b>: it did not pass, even with ZNE. The classical
      baseline is drawn as a dashed line but is not part of the pass rule.
    </p>
  )
}
