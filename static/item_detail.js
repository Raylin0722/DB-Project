function openRejectModal(reportId) {
  const modal = new bootstrap.Modal(document.getElementById('rejectModal'));
  const checkboxContainer = document.getElementById('reject-reason-list');
  const reportIdInput = document.getElementById('reject-report-id');

  const REJECT_REASONS = [
    '無意義或測試貼文',
    '垃圾廣告內容',
    '非失物相關內容',
    '重複貼文洗版',
    '張貼不雅或冒犯內容',
    '涉嫌冒用他人聯絡資訊'
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
    formData.append('fid', reportId);
    formData.append('reasons', reasons);

    const res = await fetch('/report', {
      method: 'POST',
      body: formData
    });

    const result = await res.json();
    if (result.status === 'success') {
        alert(result.message);
        confirmRejectBtn.disabled = false;
        cancelRejectBtn.disabled = false;
        confirmRejectBtn.textContent = '確認檢舉';
        cancelRejectBtn.setAttribute('data-bs-dismiss', 'modal');
        window.location.href = '/browse';
    } else { 
        alert('送出失敗');
        confirmRejectBtn.disabled = false;
        cancelRejectBtn.disabled = false;
        confirmRejectBtn.textContent = '確認駁回';
        cancelRejectBtn.setAttribute('data-bs-dismiss', 'modal');
    }
  });
});