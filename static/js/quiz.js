(() => {
  const root      = document.getElementById('quiz-root');
  const form      = document.getElementById('quiz-form');
  const timerEl   = document.getElementById('quiz_timer');
  const fill      = document.getElementById('progress_fill');
  const counter   = document.getElementById('counter');
  const modal     = document.getElementById('resultModal');
  const modalIcon = document.getElementById('modalIcon');
  const modalTitle= document.getElementById('modalTitle');
  const modalScore= document.getElementById('modalScore');
  const modalDesc = document.getElementById('modalDesc');

  const steps = document.querySelectorAll('.step');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const submitBtn = document.getElementById('submitBtn');

  let current = 0;
  const total = steps.length;

  function showStep(idx) {
    steps.forEach((s,i) => s.style.display = (i===idx ? 'block':'none'));
    counter.textContent = idx+1;

    prevBtn.disabled = idx===0;
    nextBtn.disabled = true;
    if(idx===total-1){
      nextBtn.style.display='none';
      submitBtn.style.display='inline-block';
      submitBtn.disabled = true;
    } else {
      nextBtn.style.display='inline-block';
      submitBtn.style.display='none';
    }

    const pct = ((idx+1)/total)*100;
    fill.style.width = pct+'%';
  }

  // === Highlight jawaban & kunci pilihan ===
  steps.forEach(step => {
    const options = step.querySelectorAll('input[type=radio]');
    const correctAnswer = step.dataset.correct?.toLowerCase();

    options.forEach(opt => {
      opt.addEventListener('change', () => {
        options.forEach(o => {
          const label = o.closest('.answer-option');
          if (o.value.toLowerCase() === correctAnswer) {
            label.classList.add('correct');
          }
          if (o.checked && o.value.toLowerCase() !== correctAnswer) {
            label.classList.add('incorrect');
          }
        });
        step.classList.add("answered");
        if (parseInt(step.dataset.step) === total-1) {
          submitBtn.disabled = false;
        } else {
          nextBtn.disabled = false;
        }
      });
    });
  });

  prevBtn.addEventListener('click',()=>{ if(current>0){ current--; showStep(current);} });
  nextBtn.addEventListener('click',()=>{ if(current<total-1){ current++; showStep(current);} });

  // === Submit pakai AJAX ===
  form.addEventListener('submit', e => {
    e.preventDefault();
    const formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData
    })
    .then(r => r.json())
    .then(res => {
      if(res.ok){
        // tampilkan hasil quiz
        modalScore.textContent = res.quiz_pct + "%";
        modalDesc.textContent  = `${res.correct_count} out of ${res.total_questions} correct`;

        if(res.has_coding){
          // Sudah ada coding score → evaluasi total
          if(res.overall_passed){
            modalIcon.textContent  = "🎉";
            modalTitle.textContent = "Congrats, You Passed!";
          } else {
            modalIcon.textContent  = "😢";
            modalTitle.textContent = "Sorry, You Didn’t Pass";
          }
        } else {
          // Baru quiz saja → belum final pass/fail
          modalIcon.textContent  = "🎉";
          modalTitle.textContent = "Assessment Complete!";
        }

        modal.classList.remove('hidden');
      } else {
        alert(res.msg || "Gagal menyimpan jawaban.");
      }
    })
    .catch(err => {
      console.error("Quiz submit error:", err);
      alert("Terjadi error submit quiz.");
    });
  });

  showStep(current);

  // === Timer ===
  const deadlineSec = root ? parseInt(root.dataset.deadline, 10) : 0;
  const endMs       = deadlineSec * 1000;

  const tick=()=>{
    if(!endMs) return;
    const left = Math.max(0,Math.floor((endMs-Date.now())/1000));
    const m=String(Math.floor(left/60)).padStart(2,'0');
    const s=String(left%60).padStart(2,'0');
    timerEl.textContent=`⏱️ ${m}:${s}`;
    if(left<=0){
      nextBtn.disabled=true; prevBtn.disabled=true; submitBtn.disabled=true;
      form.requestSubmit(); // auto submit via fetch
    } else { setTimeout(tick,1000); }
  };
  tick();
})();
