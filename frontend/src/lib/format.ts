/** 0.5 -> "50%", 0.00098 -> "0.10%" */
export function percent(value: number): string {
  const decimals = value > 0 && value < 0.01 ? 2 : 1
  return `${(value * 100).toFixed(decimals).replace(/\.0$/, '')}%`
}
