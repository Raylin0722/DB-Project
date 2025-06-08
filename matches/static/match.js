const lostItemsMap = {};
const foundItemsMap = {};

// 用 Lost ID 取得該失物與所有拾獲物，並找配對
async function fetchByLostID(lostId) {
	try {
		const res = await fetch(`/api/match?lost_id=${lostId}`);
		if (!res.ok) throw new Error('無法取得資料');

		const data = await res.json();

		if (data.error) {
			console.error('錯誤:', data.error);
			alert(data.error);
			return;
		}

		// 清空並放入最新失物資料
		clearMap(lostItemsMap);
		lostItemsMap[data.latestLost.lost_id] = data.latestLost;

		// 清空並放入所有拾獲物資料
		clearMap(foundItemsMap);
		data.foundItems.forEach(item => {
			foundItemsMap[item.found_id] = item;
		});

		console.log('最新失物資料:', lostItemsMap);
		console.log('所有拾獲物資料:', foundItemsMap);

		const matchedFoundItems = matchFoundByLost(lostItemsMap, foundItemsMap);
		displayMatchResults(matchedFoundItems); // 此處為結果 需修改

	} catch (err) {
		console.error('錯誤:', err);
		alert('取得資料發生錯誤');
	}
}

// 失物配對拾獲物
function matchFoundByLost(lostItems, foundItems) {
	const lostItem = Object.values(lostItems)[0];
	if (!lostItem) {
		console.log('沒有最新失物資料');
		return [];
	}

	const matches = [];
	const lostTime = new Date(lostItem.lost_time);

	for (const foundId in foundItems) {
		const foundItem = foundItems[foundId];
		const foundTime = new Date(foundItem.found_time);

		if (
			lostItem.category && foundItem.category &&
			lostItem.lost_campus && foundItem.found_campus &&
			lostItem.lost_location && foundItem.found_location
		) {
			// 比對 category、campus、location 是否相同（忽略大小寫）
			const categoryMatch = lostItem.category.toLowerCase() === foundItem.category.toLowerCase();
			const campusMatch = lostItem.lost_campus.toLowerCase() === foundItem.found_campus.toLowerCase();
			const locationMatch = lostItem.lost_location.toLowerCase() === foundItem.found_location.toLowerCase();

			// 判斷時間差（毫秒轉天）
			const diffDays = Math.abs(foundTime - lostTime) / (1000 * 60 * 60 * 24);

			if (categoryMatch && campusMatch && locationMatch && diffDays <= 3) {
				matches.push(foundItem);
			}
		}
	}

	console.log(`配對結果：共找到 ${matches.length} 筆符合的拾獲物`, matches);
	return matches;
}

// 用 Found ID 取得該拾獲物與所有失物，並找配對
async function fetchByFoundId(foundId) {
	try {
		const res = await fetch(`/api/match/lost_by_found?found_id=${foundId}`);
		if (!res.ok) throw new Error('無法取得資料');

		const data = await res.json();

		if (data.error) {
			console.error('錯誤:', data.error);
			alert(data.error);
			return;
		}

		// 清空並放入找到的失物清單
		clearMap(lostItemsMap);
		data.lostItems.forEach(item => {
			lostItemsMap[item.lost_id] = item;
		});

		console.log('找到的失物資料:', lostItemsMap);

		// 取得拾獲物資料，用於配對
		const foundItem = data.foundItem;
		if (!foundItem) {
			alert('找不到對應的拾獲物資料');
			return;
		}

		clearMap(foundItemsMap);
		foundItemsMap[foundItem.found_id] = foundItem;

		const matchedLostItems = matchLostByFound(foundItemsMap, lostItemsMap);
		displayMatchResults(matchedLostItems); // 此處為結果 需修改

	} catch (err) {
		console.error('錯誤:', err);
		alert('取得資料發生錯誤');
	}
}

// 拾獲物配對失物
function matchLostByFound(foundItems, lostItems) {
	const foundItem = Object.values(foundItems)[0];
	if (!foundItem) {
		console.log('沒有最新拾獲物資料');
		return [];
	}

	const matches = [];
	const foundTime = new Date(foundItem.found_time);

	for (const lostId in lostItems) {
		const lostItem = lostItems[lostId];
		const lostTime = new Date(lostItem.lost_time);

		if (
			foundItem.category && lostItem.category &&
			foundItem.found_campus && lostItem.lost_campus &&
			foundItem.found_location && lostItem.lost_location
		) {
			const categoryMatch = foundItem.category.toLowerCase() === lostItem.category.toLowerCase();
			const campusMatch = foundItem.found_campus.toLowerCase() === lostItem.lost_campus.toLowerCase();
			const locationMatch = foundItem.found_location.toLowerCase() === lostItem.lost_location.toLowerCase();

			const diffDays = Math.abs(foundTime - lostTime) / (1000 * 60 * 60 * 24);

			if (categoryMatch && campusMatch && locationMatch && diffDays <= 3) {
				matches.push(lostItem);
			}
		}
	}

	console.log(`反向配對結果：共找到 ${matches.length} 筆符合的失物`, matches);
	return matches;
}

// 顯示配對結果
function displayMatchResults(matches) {
	const resultEl = document.getElementById('matchResult');
	if (matches.length === 0) {
		resultEl.textContent = '沒有找到符合的配對。';
	} else {
		resultEl.textContent = JSON.stringify(matches, null, 2);
	}
}

// 清空物件內容的輔式函式
function clearMap(mapObj) {
	Object.keys(mapObj).forEach(key => delete mapObj[key]);
}

// 綁定按鈕事件
document.getElementById('fetchBtn').addEventListener('click', () => {
	const lostId = document.getElementById('lostIdInput').value.trim();
	if (!lostId) {
		alert('請輸入 Lost ID');
		return;
	}
	clearMap(lostItemsMap);
	clearMap(foundItemsMap);

	fetchByLostID(lostId);
});

document.getElementById('fetchByFoundBtn').addEventListener('click', () => {
	const foundId = document.getElementById('foundIdInput').value.trim();
	if (!foundId) {
		alert('請輸入 Found ID');
		return;
	}
	clearMap(lostItemsMap);
	clearMap(foundItemsMap);

	fetchByFoundId(foundId);
});
