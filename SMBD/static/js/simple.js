// Simple realtime UI script
const API = {
  data: '/data'
};

function qs(id){return document.getElementById(id)}

async function setStatus(){
  try{
    const res = await fetch('/health');
    const status = await res.json();
    qs('camera-status').textContent = `Camera: ${status.camera || '-'}`;
    qs('db-status').textContent = `DB: ${status.database || '-'}`;
    qs('model-status').textContent = `Model: ${status.model || '-'}`;
  }catch(e){
    qs('camera-status').textContent = 'Camera: -';
    qs('db-status').textContent = 'DB: -';
    qs('model-status').textContent = 'Model: -';
  }
}

function fmtTime(ts){
  const d = new Date(ts);
  return d.toLocaleString('id-ID', { hour: '2-digit', minute:'2-digit', second:'2-digit' });
}

function updateUI(payload){
  if(!payload || !payload.recent_detections) return;
  const arr = payload.recent_detections;

  // total deteksi dari server (akumulasi devices)
  qs('total-detections').textContent = payload.total_detections ?? 0;

  // rata-rata delay & jitter
  const delays = arr.map(x => Number(x.delay) || 0);
  const jitters = arr.map(x => Number(x.jitter) || 0);
  const avg = a => a.length ? (a.reduce((s,v)=>s+v,0)/a.length) : 0;
  const avgDelay = avg(delays);
  const avgJitter = avg(jitters);
  qs('avg-delay').textContent = `${avgDelay.toFixed(1)} ms`;
  qs('avg-jitter').textContent = `${avgJitter.toFixed(1)} ms`;

  // FPS estimasi
  const fps = avgDelay > 0 ? Math.min(Math.round(1000/avgDelay), 30) : 0;
  qs('fps').textContent = String(fps);

  // Hitung jumlah orang yang terdeteksi di frame saat ini
  // Ambil data terbaru (jika ada) untuk hitung jumlah orang
  const currentHuman = arr.length > 0 && arr[0].human_count !== undefined 
    ? arr[0].human_count 
    : 0;
  qs('human-count').textContent = String(currentHuman);

  // table
  const tbody = qs('detections-tbody');
  tbody.innerHTML = '';
  arr.slice(0,10).forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${fmtTime(item.timestamp)}</td>
      <td>${item.status}</td>
      <td>${(Number(item.delay)||0).toFixed(1)}</td>
      <td>${(Number(item.jitter)||0).toFixed(1)}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function tick(){
  try{
    const res = await fetch(API.data);
    const data = await res.json();
    updateUI(data);
  }catch(e){
    // silent retry
  }
}

function main(){
  setStatus();
  tick();
  setInterval(tick, 2000);
  setInterval(setStatus, 5000); // Update status tiap 5 detik
}

document.addEventListener('DOMContentLoaded', main);
