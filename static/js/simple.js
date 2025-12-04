(function(){
  const $ = (s)=>document.querySelector(s);
  const fmt = (n)=>typeof n==='number'?Number(n).toFixed(1):n;

  async function getJSON(url){
    try{
      const r = await fetch(url, {cache:'no-store'});
      if(!r.ok) throw new Error(r.statusText);
      return await r.json();
    }catch(e){
      console.error('fetch error', url, e);
      return null;
    }
  }

  async function refreshHealth(){
    const h = await getJSON('/health');
    if(!h) return;
    $('#camera-status').textContent = 'Camera: ' + (h.camera||'-');
    $('#db-status').textContent = 'DB: ' + (h.database||'-');
    $('#model-status').textContent = 'Model: ' + (h.model||'-');
  }

  let fpsCounter = {last: performance.now(), frames:0};
  function tickFps(){
    const now = performance.now();
    fpsCounter.frames++;
    if(now - fpsCounter.last >= 1000){
      const fps = fpsCounter.frames;
      fpsCounter.frames = 0;
      fpsCounter.last = now;
      const el = document.getElementById('fps');
      if(el) el.textContent = String(fps);
    }
    requestAnimationFrame(tickFps);
  }

  async function refreshData(){
    const d = await getJSON('/data');
    if(!d) return;
    const hc = document.getElementById('human-count');
    if(hc) hc.textContent = d.human_count ?? 0;
    const td = document.getElementById('total-detections');
    if(td) td.textContent = d.total_detections ?? 0;

    // Optional averages if present in payload
    const avgDelay = document.getElementById('avg-delay');
    const avgJitter = document.getElementById('avg-jitter');
    if(Array.isArray(d.recent_detections)){
      const list = d.recent_detections;
      const delays = list.map(x=>x.delay).filter(Number.isFinite);
      const jitters = list.map(x=>x.jitter).filter(Number.isFinite);
      if(avgDelay) avgDelay.textContent = (delays.length?fmt(delays.reduce((a,b)=>a+b,0)/delays.length):0)+' ms';
      if(avgJitter) avgJitter.textContent = (jitters.length?fmt(jitters.reduce((a,b)=>a+b,0)/jitters.length):0)+' ms';

      const tbody = document.getElementById('detections-tbody');
      if(tbody){
        tbody.innerHTML = '';
        list.forEach(item=>{
          const tr = document.createElement('tr');
          const imgSrc = (item.id!=null)?`/detection_image/${item.id}`:'';
          tr.innerHTML = `
            <td>${imgSrc?`<img src="${imgSrc}" alt="thumb" style="width:80px;height:auto;border-radius:4px;object-fit:cover;" />`:''}</td>
            <td>${item.timestamp??'-'}</td>
            <td>${item.status??'-'}</td>
            <td>${fmt(item.delay??0)}</td>
            <td>${fmt(item.jitter??0)}</td>
          `;
          tbody.appendChild(tr);
        });
      }
    }
  }

  // kick off
  refreshHealth();
  refreshData();
  setInterval(refreshHealth, 5000);
  setInterval(refreshData, 2000);
  requestAnimationFrame(tickFps);
})();
