function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById(id);
  if(el) el.classList.add('active');
  window.scrollTo({top:0, behavior:'smooth'});
}

function filterTable() {
  const q = document.getElementById('rutSearch').value.trim().toLowerCase();
  document.querySelectorAll('#alumnosTable tbody tr').forEach(r=>{
    const rut = r.cells[0].innerText.toLowerCase();
    r.style.display = (q === '' || rut.includes(q)) ? '' : 'none';
  });
}

function openDetalle(rut,nombre,sede,correo) {
  document.getElementById('detalleRut').innerText = rut || '-';
  document.getElementById('detalleNombre').innerText = nombre || '-';
  document.getElementById('detalleSede').innerText = sede || '-';
  document.getElementById('detalleCorreo').innerText = correo || '-';

  document.getElementById('detalleAvatar').src = "/static/Icon/avatar.png";

  showScreen('screen-detalle');
  renderCharts();
}

let chartsRendered=false;
function renderCharts(){
  if(chartsRendered) return;
  chartsRendered=true;

  const ctx1=document.getElementById('chartEmociones').getContext('2d');
  new Chart(ctx1,{
    type:'pie',
    data:{
      labels:['Feliz','Triste','Ansioso','Motivado'],
      datasets:[{
        data:[45,25,15,15],
        backgroundColor:['#198754','#dc3545','#ffc107','#0d6efd']
      }]
    },
    options:{responsive:true,plugins:{legend:{position:'bottom'}}}
  });

  const ctx2=document.getElementById('chartEstados').getContext('2d');
  new Chart(ctx2,{
    type:'radar',
    data:{
      labels:['Energía','Concentración','Ánimo','Motivación','Sueño'],
      datasets:[{
        label:'Estado Actual',
        data:[80,60,70,85,55],
        fill:true,
        backgroundColor:'rgba(25,135,84,0.2)',
        borderColor:'#198754',
        pointBackgroundColor:'#198754'
      }]
    },
    options:{
      responsive:true,
      scales:{r:{angleLines:{color:'#ddd'},grid:{color:'#eee'}}}
    }
  });
}
