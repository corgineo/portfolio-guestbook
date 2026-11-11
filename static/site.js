// 현재 단계 표시
const stepLinks = [...document.querySelectorAll('#steps a')];
if ('IntersectionObserver' in window) {
  const spy = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      stepLinks.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
      const on = stepLinks.find(a => a.classList.contains('on'));
      const nav = document.getElementById('steps');
      if (on && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = on.offsetLeft - nav.clientWidth / 2 + on.offsetWidth / 2;
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  stepLinks.forEach(a => { const s = document.querySelector(a.getAttribute('href')); if (s) spy.observe(s); });
}

// 복사 버튼
document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const text = document.getElementById(button.dataset.copy).textContent;
    try { await navigator.clipboard.writeText(text); button.textContent = '복사했어요'; }
    catch { button.textContent = '직접 선택해서 복사해 주세요'; }
    setTimeout(() => { button.textContent = '복사'; }, 1600);
  });
});

// 점수 계산: 총점 = Σ(가중치 × 점수 ÷ 5)
const calc = document.getElementById('calc');
function updateScores() {
  const weights = [...calc.querySelectorAll('tr.w input')].map(i => Number(i.value) || 0);
  const sum = weights.reduce((a, b) => a + b, 0);
  document.getElementById('wsum').textContent = sum === 100 ? '(합 100)' : `(합 ${sum}, 100이어야 함)`;
  let best = -1, bestRow = null;
  calc.querySelectorAll('tr.r').forEach(row => {
    row.classList.remove('top');
    let total = 0, valid = sum === 100;
    row.querySelectorAll('input[type=number]').forEach((input, i) => {
      const score = Number(input.value);
      if (!(score >= 1 && score <= 5)) valid = false;
      total += weights[i] * score / 5;
    });
    row.querySelector('output').textContent = valid ? Math.round(total) : '–';
    if (valid && total > best) { best = total; bestRow = row; }
  });
  if (bestRow) bestRow.classList.add('top');
}
calc.addEventListener('input', updateScores);
updateScores();

// 이미지 크게 보기
const zoom = document.getElementById('zoom');
document.querySelectorAll('img.zoomable').forEach(img => {
  img.addEventListener('click', () => { zoom.firstElementChild.src = img.src; zoom.firstElementChild.alt = img.alt; zoom.classList.add('on'); });
});
zoom.addEventListener('click', () => zoom.classList.remove('on'));
addEventListener('keydown', e => { if (e.key === 'Escape') zoom.classList.remove('on'); });

// 방명록
const list = document.getElementById('entries');
const listStatus = document.getElementById('list-status');
const statusText = document.getElementById('status');

async function loadEntries() {
  listStatus.textContent = '불러오는 중';
  try {
    const response = await fetch('/guestbook');
    if (!response.ok) throw Error('목록을 불러오지 못했어요.');
    const entries = await response.json();
    list.replaceChildren();
    for (const entry of entries) {
      const li = document.createElement('li');
      const name = document.createElement('strong');
      const date = document.createElement('small');
      const content = document.createElement('p');
      name.textContent = entry.name;
      date.textContent = '  ' + new Date(entry.created_at).toLocaleDateString('ko-KR');
      content.textContent = entry.content;
      li.append(name, date, content);
      list.append(li);
    }
    listStatus.textContent = entries.length ? `글 ${entries.length}개` : '아직 글이 없어요.';
  } catch (error) {
    listStatus.textContent = error.message;
  }
}

document.getElementById('refresh').addEventListener('click', loadEntries);
document.getElementById('form').addEventListener('submit', async event => {
  event.preventDefault();
  const name = document.getElementById('name').value.trim();
  const content = document.getElementById('content').value.trim();
  const button = document.getElementById('submit');
  if (!name || !content) { statusText.textContent = '이름과 내용을 적어 주세요.'; return; }
  button.disabled = true;
  statusText.textContent = '저장 중';
  try {
    const response = await fetch('/guestbook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, content }),
    });
    if (!response.ok) throw Error(response.status === 422 ? '이름은 10자, 내용은 500자까지예요.' : '저장하지 못했어요. 다시 시도해 주세요.');
    document.getElementById('content').value = '';
    statusText.textContent = '남겼어요.';
    await loadEntries();
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
loadEntries();
