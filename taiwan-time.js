// Calendar dates are computed from the Asia/Taipei clock, never the Render UTC clock.
export const ZONE='Asia/Taipei';
const WEEKDAYS=['星期日','星期一','星期二','星期三','星期四','星期五','星期六'];
function parts(now){const entries=new Intl.DateTimeFormat('en-US',{timeZone:ZONE,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(now);return Object.fromEntries(entries.filter(x=>x.type!=='literal').map(x=>[x.type,Number(x.value)]));}
function utcDate(p){return new Date(Date.UTC(p.year,p.month-1,p.day));}
function iso(d){return d.toISOString().slice(0,10);}
function add(d,n){return new Date(d.getTime()+n*86400000);}
function fmt(d){return `${d.getUTCFullYear()}年${d.getUTCMonth()+1}月${d.getUTCDate()}日（${WEEKDAYS[d.getUTCDay()]}）`;}
export function taiwanCalendar(now=new Date()){
 const p=parts(now),today=utcDate(p),weekday=today.getUTCDay(),monday=add(today,-((weekday+6)%7)),sunday=add(monday,6);
 const lastMonday=add(monday,-7),nextMonday=add(monday,7);
 return {timezone:ZONE,today:iso(today),weekday:WEEKDAYS[weekday],time:`${String(p.hour).padStart(2,'0')}:${String(p.minute).padStart(2,'0')}`,weekStart:iso(monday),weekEnd:iso(sunday),lastWeekStart:iso(lastMonday),lastWeekEnd:iso(add(lastMonday,6)),nextWeekStart:iso(nextMonday),nextWeekEnd:iso(add(nextMonday,6)),todayLabel:fmt(today),weekLabel:`${fmt(monday)}至${fmt(sunday)}`,lastWeekLabel:`${fmt(lastMonday)}至${fmt(add(lastMonday,6))}`,nextWeekLabel:`${fmt(nextMonday)}至${fmt(add(nextMonday,6))}`};
}
export function calendarQuestion(q){return /本週|這週|本周|這周|上週|上周|下週|下周|這個星期|這禮拜|下個星期|下禮拜|上個星期|上禮拜|星期幾|禮拜幾|週幾|今天幾號|今日幾號|今天日期|今日日期|今天星期|今日星期|現在幾點|當地時間|當地幾點/.test(q)}
export function getCalendarReply(q,now=new Date()){
 const c=taiwanCalendar(now);
 if(/本週|這週|本周|這周|這個星期|這禮拜/.test(q))return `以台灣時間（${ZONE}）、星期一至星期日計算，本週是 ${c.weekLabel}。\n今天是 ${c.todayLabel}。`+( /行事曆|活動|公告|考試|課表|賽程|學校|有什麼|有哪些/.test(q)?'\n這是本週的日期範圍，不代表已查到學校本週活動；學校行程仍需查閱最新校方行事曆。':'');
 if(/上週|上周|上個星期|上禮拜/.test(q))return `以台灣時間計算，上週是 ${c.lastWeekLabel}。`;
 if(/下週|下周|下個星期|下禮拜/.test(q))return `以台灣時間計算，下週是 ${c.nextWeekLabel}。`;
 if(/現在幾點|當地時間|當地幾點/.test(q))return `現在台灣時間是 ${c.todayLabel} ${c.time}（${ZONE}）。`;
 if(/星期幾|禮拜幾|週幾|今天幾號|今日幾號|今天日期|今日日期|今天星期|今日星期/.test(q))return `今天是台灣時間 ${c.todayLabel}。`;
 return null;
}
