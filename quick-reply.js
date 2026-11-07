import {getCalendarReply} from './taiwan-time.js';
export async function getQuickReply(query){return getCalendarReply(String(query||''));}
