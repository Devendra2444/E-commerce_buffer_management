const $=s=>document.querySelector(s);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

// ENGINE START
async function simulate(p,lat,onEvent){
  const st={stock:p.stock,events:[],locked:false,q:[]};
  const check=p.prot>=2,useLock=p.prot===3;
  const acquire=()=>new Promise(r=>{if(!st.locked){st.locked=true;r()}else st.q.push(r)});
  const release=()=>{const n=st.q.shift();n?n():(st.locked=false)};
  const rec=(actor,kind,seen,before,after)=>{const e={actor,kind,seen,before,after};st.events.push(e);if(onEvent)onEvent(e,st.stock)};
  async function op(actor,kind){
    if(useLock)await acquire();
    try{
      let seen=null;
      if(check){seen=st.stock;if(kind==='ship'?seen>=p.cap:seen<=0){rec(actor,kind+'_refused',seen,seen,seen);return}}
      await sleep(lat);
      const before=st.stock;st.stock+=kind==='ship'?1:-1;rec(actor,kind,seen,before,st.stock);
    }finally{if(useLock)release()}
  }
  const actor=async(name,kind,n)=>{for(let i=0;i<n;i++)await op(name,kind)};
  const jobs=[];
  for(let i=1;i<=p.ns;i++)jobs.push(actor('Seller #'+i,'ship',p.ps));
  for(let i=1;i<=p.nb;i++)jobs.push(actor('Buyer #'+i,'buy',p.pb));
  await Promise.all(jobs);
  return st;
}
function analyze(st,p){
  const ev=st.events,check=p.prot>=2,out=[];
  const over=ev.filter(e=>e.kind==='ship'&&e.after>p.cap);
  const under=ev.filter(e=>e.kind==='buy'&&e.after<0);
  if(over.length&&!check)out.push({key:'OVERFLOW',title:'Buffer overflow',why:`The warehouse holds ${p.cap} items but reached ${Math.max(...over.map(e=>e.after))}. Sellers kept shipping and nobody checked if there was free space.`});
  if(under.length&&!check)out.push({key:'UNDERFLOW',title:'Buffer underflow',why:`${under.length} order(s) were accepted for items that were not in stock (stock dropped to ${Math.min(...under.map(e=>e.after))}). Buyers clicked Buy and nobody checked if anything was left, so ghost orders were created.`});
  const race=[];
  if(over.length&&check)race.push(`${over.length} shipment(s) pushed stock above ${p.cap}: several sellers looked, all saw free space, and all shipped at the same time.`);
  if(under.length&&check)race.push(`${under.length} order(s) were confirmed for items that were already gone: several buyers looked, all saw stock available, and all bought at the same time.`);
  if(race.length)out.push({key:'RACE',title:'Race condition',why:race.join(' ')+' Each check was correct on its own, but nothing stopped others from acting between the check and the change.'});
  return out;
}
// ENGINE END

const EXAMPLES=[
 {name:'Overflow',about:'Full warehouse (5/5), 3 sellers ship 1 each. No checks.',cap:5,stock:5,ns:3,ps:1,nb:0,pb:0,prot:1,expect:['OVERFLOW']},
 {name:'Underflow',about:'1 item left, 2 buyers click Buy. No checks.',cap:5,stock:1,ns:0,ps:0,nb:2,pb:1,prot:1,expect:['UNDERFLOW']},
 {name:'Race (oversell)',about:'1 iPhone left, 2 buyers look together. Checks, no lock.',cap:5,stock:1,ns:0,ps:0,nb:2,pb:1,prot:2,expect:['RACE']},
 {name:'Race (overflow)',about:'Room for 1 more (4/5), 3 sellers look together. Checks, no lock.',cap:5,stock:4,ns:3,ps:1,nb:0,pb:0,prot:2,expect:['RACE']},
 {name:'No problem (full protection)',about:'The iPhone case with checks plus a lock.',cap:5,stock:1,ns:0,ps:0,nb:2,pb:1,prot:3,expect:[]},
 {name:'No problem (light traffic)',about:'Lots of room and stock, nothing can break.',cap:10,stock:2,ns:2,ps:2,nb:1,pb:1,prot:1,expect:[]}
];

let busy=false;
function readInputs(){
  const g=id=>Math.floor(Number($('#'+id).value));
  const p={cap:g('cap'),stock:g('stock'),ns:g('ns'),ps:g('ps'),nb:g('nb'),pb:g('pb'),prot:Number(document.querySelector('input[name=prot]:checked').value)};
  if(Object.values(p).some(v=>!Number.isFinite(v)||v<0))return{error:'Enter whole numbers of 0 or more in every field.'};
  if(p.cap<1)return{error:'Capacity must be at least 1.'};
  if(p.cap>20||p.stock>20||p.ns>10||p.nb>10||p.ps>10||p.pb>10)return{error:'Limits: capacity and stock up to 20, sellers, buyers and items up to 10.'};
  if(p.stock>p.cap)return{error:`Starting stock cannot be more than capacity (${p.cap}).`};
  return{p};
}
function drawShelf(stock,cap){
  $('#stk').textContent=stock;$('#stk').className='num big'+(stock<0||stock>cap?' bad':'');
  let h='';const n=Math.max(cap,stock);
  for(let i=0;i<n;i++)h+=`<div class="slot ${i<stock?(i>=cap?'over':'full'):''}"></div>`;
  $('#shelf').innerHTML=h;
}
function line(e,p){
  const li=document.createElement('li');
  const k=e.kind;
  if(k==='ship'){li.textContent=`${e.actor} shipped 1 → stock ${e.after}`;if(e.after>p.cap){li.className='bad';li.textContent+='  ⚠ over capacity'}}
  else if(k==='buy'){li.textContent=`${e.actor} sold 1 → stock ${e.after}`;if(e.after<0){li.className='bad';li.textContent+='  ⚠ item did not exist'}}
  else{li.className='ref';li.textContent=k==='ship_refused'?`${e.actor} shipment refused (warehouse full)`:`${e.actor} order refused (sold out)`}
  return li;
}
function showResult(st,p,problems){
  const c=k=>st.events.filter(e=>e.kind===k).length;
  $('#nums').innerHTML=[['Capacity',p.cap],['Start',p.stock],['Final stock',st.stock],['Shipments done',c('ship')],['Orders done',c('buy')],['Refused safely',c('ship_refused')+c('buy_refused')]]
   .map(([a,b])=>`<div>${a}<b>${b}</b></div>`).join('');
  $('#verdicts').innerHTML=problems.length
   ?problems.map(x=>`<div class="verdict fail"><h3 class="bad">✗ ${x.title}</h3><p><b>Why:</b> ${x.why}</p></div>`).join('')
   :`<div class="verdict pass"><h3 class="good">✓ No buffer problem</h3><p>Stock always stayed between 0 and ${p.cap}.${c('ship_refused')+c('buy_refused')?' Extra shipments or orders were refused, which is the correct, safe behaviour.':''}</p></div>`;
  $('#res').hidden=false;
}
async function run(p){
  if(busy)return;busy=true;$('#run').disabled=true;$('#err').textContent='';
  $('#res').hidden=true;$('#tl').innerHTML='';drawShelf(p.stock,p.cap);
  if(p.ns*p.ps+p.nb*p.pb===0)$('#tl').innerHTML='<li class="ref">Nobody ships or buys, so nothing can go wrong.</li>';
  const st=await simulate(p,600,(e,s)=>{$('#tl').append(line(e,p));$('#tl').scrollTop=1e6;drawShelf(s,p.cap)});
  showResult(st,p,analyze(st,p));
  busy=false;$('#run').disabled=false;
}
function fill(p){for(const k of['cap','stock','ns','ps','nb','pb'])$('#'+k).value=p[k];document.querySelector(`input[name=prot][value="${p.prot}"]`).checked=true}

$('#run').onclick=()=>{const r=readInputs();if(r.error){$('#err').textContent=r.error;return}run(r.p)};
$('#ex').innerHTML=EXAMPLES.map((x,i)=>`<button data-i="${i}"><b>${x.name}</b><span class="hint">${x.about}</span></button>`).join('');
$('#ex').onclick=e=>{const b=e.target.closest('button');if(!b)return;const x=EXAMPLES[b.dataset.i];fill(x);run(x);window.scrollTo({top:0,behavior:'smooth'})};
$('#verify').onclick=async()=>{
  const btn=$('#verify');btn.disabled=true;const rows=[];
  for(const x of EXAMPLES){
    const st=await simulate(x,15);
    const got=analyze(st,x).map(a=>a.key).sort();
    const exp=[...x.expect].sort();
    rows.push({name:x.name,exp:exp.join('+')||'NONE',got:got.join('+')||'NONE',ok:exp.join()===got.join()});
  }
  const keys=new Set(rows.filter(r=>r.ok).flatMap(r=>r.got.split('+')));
  const all=rows.every(r=>r.ok)&&['OVERFLOW','UNDERFLOW','RACE'].every(k=>keys.has(k));
  $('#vt').innerHTML=`<table><tr><th>Example</th><th>Expected</th><th>Detected</th><th>Status</th></tr>`+
   rows.map(r=>`<tr><td>${r.name}</td><td>${r.exp}</td><td>${r.got}</td><td class="${r.ok?'good':'bad'}">${r.ok?'PASS ✓':'FAIL ✗'}</td></tr>`).join('')+
   `</table><p class="${all?'good':'bad'}"><b>${all?'✓ All three buffer cases (overflow, underflow, race) were triggered and detected correctly.':'✗ Something did not match.'}</b></p>`;
  btn.disabled=false;
};
drawShelf(1,5);
