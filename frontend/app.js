console.log("✅ app.js 載入成功");
const map = L.map('map').setView([25.0330, 121.5654], 13);

L.tileLayer('http://localhost:8080/tile/{z}/{x}/{y}.png', {
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
document.getElementById("user-location-input").addEventListener("focus", () => {
  pickingUserLocation = true;
  map.getContainer().style.cursor = 'crosshair';
});

map.on('click', (e) => {
  if (pickingUserLocation) {
    const { lat, lng } = e.latlng;
    document.getElementById("user-location-input").value = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    
    if (userLocationMarker) map.removeLayer(userLocationMarker);
    userLocationMarker = L.marker([lat, lng], { color: 'green' })
      .addTo(map)
      .bindPopup("目前位置")
      .openPopup();

    pickingUserLocation = false;
    map.getContainer().style.cursor = '';
  }
});

// confirmUserLocation
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
    fetch("http://localhost/api/users/", {
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

  if (isCoords) {
    const [lat, lng] = tryCoords;
    handleLatLng(lat, lng); // 直接走經緯度
  } else {
    geocodeAddress(loc).then(coord => { // 若是地址字串，使用 geocode 解析成經緯度
      if (!coord) {
        alert("找不到該地址，請重新輸入");
        return;
      }
      const [lat, lng] = coord;
      handleLatLng(lat, lng);
    });
  }
}

// === 找附近使用者 ===
function fetchNearbyUsers() {
  const username = document.getElementById("username-input").value;
  const radius = parseFloat(document.getElementById("radius-input").value || "2");
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

  fetch(`http://localhost/api/users/nearby/?name=${encodeURIComponent(username)}&radius=${radius}`)
    .then(res => res.json())
    .then(data => {
      const listEl = document.getElementById("nearby-users-list");
      listEl.innerHTML = '';

      if (data.nearby.length === 0) {
        listEl.innerHTML = '<li>查無附近使用者</li>';
        return;
      }

      data.nearby.forEach(u => {
        const li = document.createElement("li");
        li.textContent = `${u.name} (${u.lat.toFixed(5)}, ${u.lng.toFixed(5)})`;
        listEl.appendChild(li);

        // 使用明顯的 marker + 名稱 label
        const userMarker = L.marker([u.lat, u.lng])
          .addTo(map)
          .bindPopup(`<strong>${u.name}</strong>`)
          .openPopup();

        // 顯示名稱 label (透過 permanent tooltip)
        userMarker.bindTooltip(u.name, {
          permanent: true,
          direction: 'top',
          offset: [0, -10],
          className: 'user-label'
        }).openTooltip();

        // 點擊 marker 開啟聊天視窗
        userMarker.on('click', () => openChat(u.name));

        // 可選擇自動移除 marker
        setTimeout(() => map.removeLayer(userMarker), 20_000); // 20秒後移除
      });
    })
    .catch(err => {
      console.error("附近使用者查詢錯誤:", err);
      alert("查詢附近使用者失敗，請稍後再試");
    });
}


// === 聊天室 ===
function openChat(targetName) {
  const yourName = document.getElementById("username-input").value.trim();
  if (!yourName || yourName === targetName) {
    alert("請輸入有效的使用者名稱，且不能和自己聊天");
    return;
  }

  currentUserName = yourName;
  currentChatUser = targetName;

  // UI
  document.getElementById("chat-box").style.display = "block";
  document.getElementById("chat-user-title").innerText = `與 ${targetName} 聊天中`;
  document.getElementById("chat-messages").innerHTML = "";

  // 建立 WebSocket
  const wsUrl = `ws://localhost/ws/chat/${yourName}/${targetName}/`;
  socket = new WebSocket(wsUrl);

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const msgDiv = document.createElement("div");
    msgDiv.innerHTML = `<strong>${data.sender_name}</strong>: ${data.message}`;
    document.getElementById("chat-messages").appendChild(msgDiv);
    document.getElementById("chat-messages").scrollTop = 99999;
  };

  socket.onclose = function () {
    console.log("WebSocket 已關閉");
    socket = null;
  };
}

function sendMessage() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (msg && socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ message: msg }));
    input.value = "";
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

  Promise.all([
    geocodeAddress(startAddress),
    geocodeAddress(endAddress)
  ]).then(([startCoord, endCoord]) => {
    if (!startCoord || !endCoord) {
      alert("找不到地址，請再試一次");
      return;
    }

    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);
    if (mainRoute) map.removeLayer(mainRoute);

    startMarker = L.marker(startCoord).addTo(map).bindPopup("起點").openPopup();
    endMarker = L.marker(endCoord).addTo(map).bindPopup("終點").openPopup();

    getRoute(startCoord, endCoord);
  });
}

function geocodeAddress(query) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;

  return fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.length === 0) return null;
      return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
    })
    .catch(err => {
      console.error("Geocoding 錯誤:", err);
      return null;
    });
}

function getRoute(start, end) {
  const url = `http://localhost:5000/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (!data.routes || data.routes.length === 0) return;

      const main = data.routes[0];
      const mainCoords = main.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
      mainRoute = L.polyline(mainCoords, { color: 'blue', weight: 5 }).addTo(map);
      document.getElementById('main-distance').innerText = `${(main.distance / 1000).toFixed(2)} km`;
      document.getElementById('main-duration').innerText = `${(main.duration / 60).toFixed(1)} 分鐘`;

      map.fitBounds(mainRoute.getBounds());
    })
    .catch(err => console.error("OSRM 錯誤:", err));
}
