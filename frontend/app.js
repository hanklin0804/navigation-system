console.log("✅ app.js 載入成功");
const map = L.map('map').setView([25.0330, 121.5654], 13);

L.tileLayer('https://34.57.158.129/tile/tile/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap',
  maxZoom: 19,
}).addTo(map);

let startMarker = null;
let endMarker = null;
let mainRoute = null;

let userLocationMarker = null;
let pickingUserLocation = false;

let socket = null;
let currentChatUser = null;
let currentUserName = null;

// === 使用者選擇自己位置 ===
// 當使用者點擊輸入框時，啟用地圖點選模式
document.getElementById("user-location-input").addEventListener("focus", () => {
  pickingUserLocation = true;
  map.getContainer().style.cursor = 'crosshair';
});

// 監聽地圖的點擊事件
map.on('click', (e) => {
  if (pickingUserLocation) { // 若正在選擇位置
    const { lat, lng } = e.latlng; // 取得使用者點擊的經緯度
    document.getElementById("user-location-input").value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    // 將經緯度顯示到輸入框中，保留小數點五位

     // 如果原本已有標記，就先移除
    if (userLocationMarker) map.removeLayer(userLocationMarker);

    // 在地圖上加上新的綠色標記，並開啟提示窗
    userLocationMarker = L.marker([lat, lng], { color: 'green' })
      .addTo(map)
      .bindPopup("目前位置")
      .openPopup();

    pickingUserLocation = false; // 關閉選點模式
    map.getContainer().style.cursor = ''; // 恢復預設游標樣式
  }
});

// === 使用者填寫「名稱」與「位置」後觸發的函式 ===
function confirmUserLocation() {
  const username = document.getElementById("username-input").value;
  const loc = document.getElementById("user-location-input").value;

  if (!username || !loc) {
    alert("請輸入使用者名稱與位置");
    return;
  }
  // 嘗試把 loc 分成 [緯度, 經度] 並轉為數字
  const tryCoords = loc.split(",").map(s => parseFloat(s.trim()));
  // 判斷是否為合法經緯度：兩個元素 + 都是數字
  const isCoords = tryCoords.length === 2 && !tryCoords.some(isNaN);

  const handleLatLng = (lat, lng) => {
    // 將格式標準化，寫回輸入框中（統一成 5 位小數）
    document.getElementById("user-location-input").value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;

    // 如果有舊的使用者位置 marker，就先移除，避免地圖上會出現很多顆重疊的 marker。
    if (userLocationMarker) map.removeLayer(userLocationMarker);
    // 在地圖上加上一顆新的 marker，並顯示使用者名稱
    userLocationMarker = L.marker([lat, lng])
      .addTo(map)
      .bindPopup(`使用者 ${username}`)
      .openPopup();

    // 把地圖視角移動到該點，並放大
    map.setView([lat, lng], 16);

    // 結束位置選擇模式，滑鼠游標恢復正常
    pickingUserLocation = false;
    map.getContainer().style.cursor = '';

    // 呼叫後端 API 儲存
    fetch("https://34.57.158.129/api/users/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: username,
        lat: lat,
        lng: lng
      })
    })
    .then(res => {
      if (!res.ok) throw new Error("伺服器儲存失敗");
      return res.json();
    })
    .then(data => {
      console.log("✅ 使用者位置已儲存到後端");
    })
    .catch(err => {
      console.error("❌ 儲存失敗", err);
      alert("儲存到伺服器失敗，請稍後再試");
    });
  };

  // 若輸入的是經緯度，直接處理
  if (isCoords) {
    const [lat, lng] = tryCoords;
    handleLatLng(lat, lng); 
  } else {
     // 否則視為地址字串，進行geocode 解析成經緯度
    geocodeAddress(loc).then(coord => { 
      if (!coord) {
        alert("找不到該地址，請重新輸入");
        return;
      }
      const [lat, lng] = coord;
      handleLatLng(lat, lng);
    });
  }
}


// === 查詢並顯示附近使用者 ===
function fetchNearbyUsers() {
  const username = document.getElementById("username-input").value;
  const radius = parseFloat(document.getElementById("radius-input").value || "2"); // 若無填，預設半徑為 2 公里
  const loc = document.getElementById("user-location-input").value;

  if (!username || !loc || isNaN(radius)) {
    alert("請確認已輸入使用者名稱、位置與半徑");
    return;
  }

  const tryCoords = loc.split(",").map(s => parseFloat(s.trim()));
  if (tryCoords.length !== 2 || tryCoords.some(isNaN)) {
    alert("請輸入正確的座標格式");
    return;
  }

  fetch(`https://34.57.158.129/api/users/nearby/?name=${encodeURIComponent(username)}&radius=${radius}`)
    .then(res => res.json())
    .then(data => {
      const listEl = document.getElementById("nearby-users-list");
      listEl.innerHTML = ''; // 清空列表區域

      if (data.nearby.length === 0) {
        listEl.innerHTML = '<li>查無附近使用者</li>';
        return;
      }

      // 對每一位附近使用者建立 UI 與地圖標記
      data.nearby.forEach(u => {
        // 在 HTML 清單中新增使用者資訊
        const li = document.createElement("li");
        li.textContent = `${u.name} (${u.lat.toFixed(5)}, ${u.lng.toFixed(5)})`;
        listEl.appendChild(li);

        // 在地圖上新增一顆 marker 並綁定 popup
        const userMarker = L.marker([u.lat, u.lng])
          .addTo(map)
          .bindPopup(`<strong>${u.name}</strong>`)
          .openPopup();

        // 顯示常駐名稱 label（上方小標籤）
        userMarker.bindTooltip(u.name, {
          permanent: true,
          direction: 'top',
          offset: [0, -10],
          className: 'user-label'
        }).openTooltip();

        // 點擊 marker 開啟聊天視窗
        userMarker.on('click', () => openChat(u.name));

        // 過 20 秒自動移除 marker，避免地圖混亂（視情況可拔）
        setTimeout(() => map.removeLayer(userMarker), 20_000); 
      });
    })
    .catch(err => {
      console.error("附近使用者查詢錯誤:", err);
      alert("查詢附近使用者失敗，請稍後再試");
    });
}


// === 聊天室功能 ===
function openChat(targetName) {
  // 取得使用者自己的名稱
  const yourName = document.getElementById("username-input").value.trim();
  
  if (!yourName || yourName === targetName) {
    alert("請輸入有效的使用者名稱，且不能和自己聊天");
    return;
  }

  // 記錄目前的使用者與聊天對象（供其他函式使用）
  currentUserName = yourName;
  currentChatUser = targetName;

  // UI 相關操作 
  document.getElementById("chat-box").style.display = "block"; // 顯示聊天區塊
  document.getElementById("chat-user-title").innerText = `與 ${targetName} 聊天中`; // 顯示聊天對象名稱
  document.getElementById("chat-messages").innerHTML = "";  // 清空歷史訊息

  // 建立 WebSocket 連線 
  const wsUrl = `wss://34.57.158.129/ws/chat/${yourName}/${targetName}/`;
  socket = new WebSocket(wsUrl);

  // 當有訊息從後端收到時觸發
  socket.onmessage = function (event) {
    const data = JSON.parse(event.data); // 將 JSON 字串轉為物件

    // 建立訊息 DOM 元素
    const msgDiv = document.createElement("div");
    msgDiv.innerHTML = `<strong>${data.sender_name}</strong>: ${data.message}`;
    
    // 加到訊息列表中
    document.getElementById("chat-messages").appendChild(msgDiv);

    // 自動捲到底（顯示最新訊息）
    document.getElementById("chat-messages").scrollTop = 99999;
  };

  // 當 WebSocket 關閉時觸發
  socket.onclose = function () {
    console.log("WebSocket 已關閉");
    socket = null;
  };
}

// 聊天室按下送出訊息按鈕時觸發
function sendMessage() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();

  // 檢查有無輸入文字，WebSocket 是否已連線成功
  if (msg && socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ message: msg }));
    input.value = ""; // 清空輸入框
  }
}

function closeChat() {
  if (socket) {
    socket.close();
    socket = null;
  }
  document.getElementById("chat-box").style.display = "none";
}


// === 路線查詢 ===
function handleAddressSubmit() {
  const startAddress = document.getElementById("start-input").value;
  const endAddress = document.getElementById("end-input").value;

  if (!startAddress || !endAddress) {
    alert("請輸入完整起點與終點地址");
    return;
  }

  // 同時進行兩個地址的地理編碼查詢
  Promise.all([
    geocodeAddress(startAddress),
    geocodeAddress(endAddress)
  ]).then(([startCoord, endCoord]) => {
    if (!startCoord || !endCoord) {
      alert("找不到地址，請再試一次");
      return;
    }

     // 清除先前地圖上已存在的 marker 和路線
    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);
    if (mainRoute) map.removeLayer(mainRoute);

    // 加上新的起點與終點 marker
    startMarker = L.marker(startCoord).addTo(map).bindPopup("起點").openPopup();
    endMarker = L.marker(endCoord).addTo(map).bindPopup("終點").openPopup();

    // 呼叫 OSRM API 進行路線規劃
    getRoute(startCoord, endCoord);
  });
}

// 將地址轉為經緯度（使用 Nominatim OpenStreetMap API）
function geocodeAddress(query) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;

  return fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.length === 0) return null;
      return [parseFloat(data[0].lat), parseFloat(data[0].lon)]; // 回傳 [lat, lng]
    })
    .catch(err => {
      console.error("Geocoding 錯誤:", err);
      return null;
    });
}

// 呼叫 OSRM API 查詢路線資訊，畫在地圖上並顯示距離與時間
function getRoute(start, end) {
  const url = `https://34.57.158.129/osrm/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (!data.routes || data.routes.length === 0) return;

      const main = data.routes[0];

      // 轉為 Leaflet 可用格式
      const mainCoords = main.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
      
      // 畫出主要路線 polyline
      mainRoute = L.polyline(mainCoords, { color: 'blue', weight: 5 }).addTo(map);
      
      // 顯示距離與預估時間
      document.getElementById('main-distance').innerText = `${(main.distance / 1000).toFixed(2)} km`;
      document.getElementById('main-duration').innerText = `${(main.duration / 60).toFixed(1)} 分鐘`;

      // 自動縮放地圖到路線範圍
      map.fitBounds(mainRoute.getBounds());
    })
    .catch(err => console.error("OSRM 錯誤:", err));
}
