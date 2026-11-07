import assert from 'node:assert/strict';
import {taiwanCalendar,getCalendarReply} from './taiwan-time.js';
const a=taiwanCalendar(new Date('2026-11-07T18:30:00Z')); // Taiwan 11/08 02:30 Sunday
assert.equal(a.today,'2026-11-08');assert.equal(a.weekStart,'2026-11-02');assert.equal(a.weekEnd,'2026-11-08');
const b=taiwanCalendar(new Date('2026-11-08T16:01:00Z')); // Taiwan Monday 00:01
assert.equal(b.today,'2026-11-09');assert.equal(b.weekStart,'2026-11-09');assert.equal(b.weekEnd,'2026-11-15');
assert.match(getCalendarReply('本周是哪幾天',new Date('2026-11-07T18:30:00Z')),/11月2日/);
assert.match(getCalendarReply('本週學校有什麼活動',new Date('2026-11-07T18:30:00Z')),/不能|仍需/);
assert.equal(getCalendarReply('如何重修',new Date('2026-11-07T18:30:00Z')),null);
console.log('V10 Taiwan time/week tests passed');
