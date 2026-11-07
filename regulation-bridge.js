// Evidence-first rendering for credit/re-take questions; does not invent school policy.
export function searchRegulationFallback(query, data) {
  if (!data || !Array.isArray(data.matches) || !data.matches.length) return null;
  const first = data.matches.find(x => /學習評量補充規定/.test(x.title || '')) || data.matches[0];
  if (!/學習評量補充規定/.test(first.title || '')) return null;
  return [
    '📚 重修／補修查詢（依校方既有文件索引）',
    '',
    '根據《' + first.title + '》的已收錄摘要：',
    '① 學期成績不及格的科目，依規定的補考基準辦理，每學期每科目補考一次。',
    '② 未取得學分者，得依相關規定申請重修或補修。',
    '',
    '⚠️ 目前的文件摘要尚不足以確認本學期的開課、報名日期、費用、申請表或個別學生資格。請向教務處註冊組確認，避免把通則當作最新公告。',
    '',
    '🔗 資料來源',
    first.source_url || '校方正式文件（連結未提供）',
    '文件名稱：' + first.title,
    '專案資料最後核對：' + (first.last_verified_date || '未標示'),
    '（上述為專案既有摘要，詳細條文與最新版本仍應以官方原文為準。）'
  ].join('\n');
}
