function openAcceptModal(reportId, rawDescription) {
  const modal = new bootstrap.Modal(document.getElementById('acceptModal'));
  const checkboxContainer = document.getElementById('accept-reason-list');
  const reportIdInput = document.getElementById('accept-report-id');

  const REASONS = [
    '無意義或測試貼文',
    '垃圾廣告內容',
    '非失物相關內容',
    '重複貼文洗版',
    '張貼不雅或冒犯內容',
    '涉嫌冒用他人聯絡資訊'
  ];

  const selectedReasons = rawDescription.split(',').map(r => r.trim());
  checkboxContainer.innerHTML = '';
  reportIdInput.value = reportId;

  REASONS.forEach(reason => {
    const id = 'reason_' + reason.replace(/\s/g, '_');
    const wrapper = document.createElement('div');
    wrapper.classList.add('form-check');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'form-check-input';
    checkbox.name = 'reason';
    checkbox.value = reason;
    checkbox.id = id;
    if (selectedReasons.includes(reason)) checkbox.checked = true;

    const label = document.createElement('label');
    label.className = 'form-check-label';
    label.htmlFor = id;
    label.textContent = reason;

    wrapper.appendChild(checkbox);
    wrapper.appendChild(label);
    checkboxContainer.appendChild(wrapper);
  });

  modal.show();
}

document.addEventListener('DOMContentLoaded', function () {
    const confirmBtn = document.getElementById('confirmAcceptBtn');
    const cancelBtn = document.getElementById('cancelAcceptBtn');
    const modalElement = document.getElementById('acceptModal'); // 補這行

    confirmBtn.addEventListener('click', async function () {
        const reportId = document.getElementById('accept-report-id').value;
        const reasons = Array.from(document.querySelectorAll('input[name="reason"]:checked'))
            .map(input => input.value)
            .join(',');

        if (reasons.length === 0) {
            alert("請至少勾選一個檢舉理由。");
            return;
        }

        confirmBtn.disabled = true;
        cancelBtn.disabled = true;
        cancelBtn.removeAttribute('data-bs-dismiss');
        confirmBtn.textContent = '處理中...';

        // 禁止 modal 關閉
        modalElement.querySelector('.btn-close')?.remove();
        modalElement.addEventListener('hide.bs.modal', function (e) {
            if (confirmBtn.disabled) e.preventDefault();
        }, { once: true });

        const formData = new FormData();
        formData.append('rid', reportId);
        formData.append('mode', 'accept');
        formData.append('reasons', reasons);

        const res = await fetch('/send_report', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();
        if (result.status === 'success') {
            alert('送出成功');
            confirmBtn.disabled = false;
            cancelBtn.disabled = false;
            confirmBtn.textContent = '確認送出';
            cancelBtn.setAttribute('data-bs-dismiss', 'modal');
            window.location.href = '/adminManage';
        } else {
            alert('送出失敗');
            confirmBtn.disabled = false;
            cancelBtn.disabled = false;
            confirmBtn.textContent = '確認送出';
            cancelBtn.setAttribute('data-bs-dismiss', 'modal');
        }
    });
});
function openRejectModal(reportId) {
  const modal = new bootstrap.Modal(document.getElementById('rejectModal'));
  const checkboxContainer = document.getElementById('reject-reason-list');
  const reportIdInput = document.getElementById('reject-report-id');

  const REJECT_REASONS = [
    '貼文內容符合規範',
    '無明顯惡意或廣告成分',
    '無違反平台使用規則',
    '檢舉理由不成立或過於模糊',
    '與實際張貼情境無關',
    '經聯繫發文者後確認為正常貼文'
  ];

  checkboxContainer.innerHTML = '';
  reportIdInput.value = reportId;

  REJECT_REASONS.forEach(reason => {
    const id = 'reject_' + reason.replace(/\s/g, '_');
    const wrapper = document.createElement('div');
    wrapper.classList.add('form-check');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'form-check-input';
    checkbox.name = 'reason';
    checkbox.value = reason;
    checkbox.id = id;

    const label = document.createElement('label');
    label.className = 'form-check-label';
    label.htmlFor = id;
    label.textContent = reason;

    wrapper.appendChild(checkbox);
    wrapper.appendChild(label);
    checkboxContainer.appendChild(wrapper);
  });

  modal.show();
}

document.addEventListener('DOMContentLoaded', function () {
  const confirmRejectBtn = document.getElementById('confirmRejectBtn');
  const cancelRejectBtn = document.getElementById('cancelRejectBtn');
  const rejectModalElement = document.getElementById('rejectModal');

  confirmRejectBtn.addEventListener('click', async function () {
    const reportId = document.getElementById('reject-report-id').value;
    const reasons = Array.from(document.querySelectorAll('#reject-reason-list input[name="reason"]:checked'))
      .map(input => input.value)
      .join(',');

    if (!reasons) {
      alert('請至少選擇一項駁回理由');
      return;
    }

    // 鎖定按鈕
    confirmRejectBtn.disabled = true;
    cancelRejectBtn.disabled = true;
    cancelRejectBtn.removeAttribute('data-bs-dismiss');
    confirmRejectBtn.textContent = '處理中...';

    // 禁止 modal 關閉
    rejectModalElement.querySelector('.btn-close')?.remove();
    rejectModalElement.addEventListener('hide.bs.modal', function (e) {
      if (confirmRejectBtn.disabled) e.preventDefault();
    }, { once: true });

    const formData = new FormData();
    formData.append('rid', reportId);
    formData.append('mode', 'reject');
    formData.append('reasons', reasons);

    const res = await fetch('/send_report', {
      method: 'POST',
      body: formData
    });

    const result = await res.json();
    if (result.status === 'success') {
        alert('已成功駁回檢舉');
        confirmRejectBtn.disabled = false;
        cancelRejectBtn.disabled = false;
        confirmRejectBtn.textContent = '確認駁回';
        cancelRejectBtn.setAttribute('data-bs-dismiss', 'modal');
        window.location.href = '/adminManage';
    } else { 
        alert('送出失敗');
        confirmRejectBtn.disabled = false;
        cancelRejectBtn.disabled = false;
        confirmRejectBtn.textContent = '確認駁回';
        cancelRejectBtn.setAttribute('data-bs-dismiss', 'modal');
    }
  });
});
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
