// UI data only: never put API keys or private data in school-ui-config.json.
(async function(){
 const target=document.getElementById('quick-categories');
 const links=document.getElementById('school-links');
 try {
  const res=await fetch('./school-ui-config.json',{cache:'no-store'});
  if(!res.ok)throw new Error('HTTP '+res.status);
  const cfg=await res.json();
  if(cfg.school?.assistantTitle){document.title=cfg.school.assistantTitle;const h=document.querySelector('.brand h1');if(h)h.textContent=cfg.school.assistantTitle;}
  if(cfg.school?.subtitle){const s=document.querySelector('.brand .sub');if(s)s.textContent=cfg.school.subtitle;}
  const welcome=document.querySelector('.welcome-title strong');if(welcome&&cfg.ui?.welcomeTitle)welcome.textContent=cfg.ui.welcomeTitle;
  const welcomeDescription=document.querySelector('.welcome > span');if(welcomeDescription&&cfg.ui?.welcomeDescription)welcomeDescription.textContent=cfg.ui.welcomeDescription;
  const footer=document.querySelector('footer');if(footer&&cfg.school?.disclaimer)footer.textContent=cfg.school.disclaimer;
  for(const group of cfg.quickCategories||[]){
   const section=document.createElement('div');section.className='tag-section';
   const title=document.createElement('div');title.className='tag-section-title';title.textContent=group.title||'快速查詢';section.append(title);
   if(group.description){const note=document.createElement('div');note.className='helper-note';note.textContent=group.description;section.append(note);}
   const wrap=document.createElement('div');wrap.className='quick-tags';
   for(const item of group.items||[]){
    if(!item.label||!item.query)continue;
    const btn=document.createElement('button');btn.type='button';btn.className='quick-tag '+(['score','credit','student','other'].includes(item.style)?item.style:'other');
    btn.dataset.query=item.query;btn.textContent=item.label;wrap.append(btn);
   }
   section.append(wrap);target.append(section);
  }
  for(const item of cfg.webButtons||[]){
   try{const u=new URL(item.url,location.href);if(!['https:','http:'].includes(u.protocol))continue;
    const a=document.createElement('a');a.className='school-link';a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=item.label||u.hostname;
    if(item.description)a.title=item.description;links.append(a);
   }catch{}
  }
 }catch(e){const warning=document.createElement('p');warning.className='config-warning';warning.textContent='快速分類設定載入失敗，仍可手動輸入問題。';target.append(warning);console.error('UI config load error',e);}
})();
