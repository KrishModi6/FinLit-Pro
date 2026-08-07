/**
 * Edge-case tests for the finance maths in src/data/market.js.
 *
 * These are the numbers the course shows to readers, so the cases that matter
 * are the degenerate ones: a flat price series, too little history, a zero in
 * the data, a currency Intl has never heard of. Run with `npm test`.
 */

const M = await import(new URL('../src/data/market.js', import.meta.url).href)
let issues = 0
const note = (label, got, expected, ok) => {
  if (!ok) { issues++; console.log(`  SUSPECT  ${label}\n           got ${JSON.stringify(got)}  expected ${expected}`) }
  else console.log(`  ok       ${label}  ->  ${JSON.stringify(got)}`)
}

console.log('--- sma ---')
note('sma of [1..5] period 3, last value = 4', M.sma([1,2,3,4,5],3).at(-1), '4', M.sma([1,2,3,4,5],3).at(-1) === 4)
note('nulls before the window fills', M.sma([1,2,3],3).slice(0,2), '[null,null]', M.sma([1,2,3],3).slice(0,2).every(v=>v===null))
note('period longer than data -> all null', M.sma([1,2],5), 'all null', M.sma([1,2],5).every(v=>v===null))
note('empty input does not throw', M.sma([],3), '[]', Array.isArray(M.sma([],3)))

console.log('\n--- rsi ---')
const up = Array.from({length:40},(_,i)=>100+i)          // monotonic rise
const down = Array.from({length:40},(_,i)=>100-i)         // monotonic fall
note('all-gains series pins to 100', M.rsi(up).at(-1), '100', M.rsi(up).at(-1) === 100)
note('all-losses series pins to 0', M.rsi(down).at(-1), '0', M.rsi(down).at(-1) === 0)
note('flat series reads neutral, not overbought', M.rsi(new Array(40).fill(50)).at(-1), '50', M.rsi(new Array(40).fill(50)).at(-1) === 50)
note('too little data -> nulls, no throw', M.rsi([1,2,3]), 'all null', M.rsi([1,2,3]).every(v=>v===null))

console.log('\n--- bollinger ---')
const flat = new Array(30).fill(10)
const b = M.bollinger(flat)
note('zero variance gives upper == lower == mean', [b.upper.at(-1), b.lower.at(-1)], '[10,10]', b.upper.at(-1)===10 && b.lower.at(-1)===10)
const bb = M.bollinger([1,2,3,4,5,6,7,8,9,10], 5, 2)
note('upper is above lower on real data', bb.upper.at(-1) > bb.lower.at(-1), 'true', bb.upper.at(-1) > bb.lower.at(-1))

console.log('\n--- maxDrawdown ---')
note('100 -> 50 is 50%', M.maxDrawdown([100,50]), '50', Math.abs(M.maxDrawdown([100,50]) - 50) < 1e-9)
note('monotonic rise is 0%', M.maxDrawdown([1,2,3,4]), '0', M.maxDrawdown([1,2,3,4]) === 0)
note('recovery still reports the trough', M.maxDrawdown([100,50,100]), '50', Math.abs(M.maxDrawdown([100,50,100]) - 50) < 1e-9)
note('empty input does not throw', M.maxDrawdown([]), '0', M.maxDrawdown([]) === 0)

console.log('\n--- annualisedStats ---')
const s = M.annualisedStats([100,101,102,103,104], 252)
note('drift and vol are finite on normal data', [Number.isFinite(s.drift), Number.isFinite(s.vol)], '[true,true]', Number.isFinite(s.drift)&&Number.isFinite(s.vol))
note('single point -> NaN not a throw', M.annualisedStats([100]).vol, 'NaN', Number.isNaN(M.annualisedStats([100]).vol))
note('zeros and negatives are skipped, no NaN leak', Number.isFinite(M.annualisedStats([100,0,-5,120,121,122]).vol), 'true', Number.isFinite(M.annualisedStats([100,0,-5,120,121,122]).vol))

console.log('\n--- formatMoney ---')
note('USD default', M.formatMoney(1234.5), '$1,234.50', M.formatMoney(1234.5) === '$1,234.50')
note('GBp converted from pence', M.formatMoney(120.5,{currency:'GBp'}), '£1.21', M.formatMoney(120.5,{currency:'GBp'}) === '£1.21')
note('unknown code does not throw', M.formatMoney(10,{currency:'XYZZY'}), 'number + code', /XYZZY/.test(M.formatMoney(10,{currency:'XYZZY'})))
note('NaN guarded', M.formatMoney(NaN), 'n/a', M.formatMoney(NaN) === 'n/a')
note('auto keeps cents under 10', M.formatMoney(5.25,{dp:'auto'}), '$5.25', M.formatMoney(5.25,{dp:'auto'}) === '$5.25')
note('auto drops cents over 10', M.formatMoney(1234.5,{dp:'auto'}), '$1,235', M.formatMoney(1234.5,{dp:'auto'}) === '$1,235')
note('auto decides AFTER pence conversion', M.formatMoney(120.5,{currency:'GBp',dp:'auto'}), '£1.21', M.formatMoney(120.5,{currency:'GBp',dp:'auto'}) === '£1.21')
note('negative values format', M.formatMoney(-42,{dp:0}), '-$42', M.formatMoney(-42,{dp:0}).includes('42'))

console.log(`\n${issues} suspect result(s)`)
