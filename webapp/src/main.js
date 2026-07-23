const routes = {
  home: { title: 'Home', render: () => '<h2>Welcome to 3D Ludo Web</h2><p>Select a module from the nav.</p>' },
  ui: { title: 'UI', render: () => '<h2>UI</h2><p>UI components and screens will live here.</p>' },
  auth: { title: 'Authentication', render: () => '<h2>Authentication</h2><p>Login and auth providers.</p>' },
  store: { title: 'Store', render: () => '<h2>Store</h2><p>In-app purchases and storefront.</p>' },
  lobby: { title: 'Lobby', render: () => '<h2>Lobby</h2><p>Matchmaking and rooms.</p>' },
  friends: { title: 'Friends', render: () => '<h2>Friends</h2><p>Friends list and invites.</p>' },
  inventory: { title: 'Inventory', render: () => '<h2>Inventory</h2><p>Player items and equipment.</p>' },
  settings: { title: 'Settings', render: () => '<h2>Settings</h2><p>User and app settings.</p>' },
  engine: { title: '3D Engine (Unity)', render: () => '<h2>3D Engine</h2><p>Unity integration and exported builds.</p>' }
}

function navLink(key, title){
  const a = document.createElement('a')
  a.href = '#'+key
  a.textContent = title
  a.onclick = (e)=>{ e.preventDefault(); navigate(key) }
  a.id = 'nav-'+key
  return a
}

function buildNav(){
  const nav = document.getElementById('nav')
  nav.innerHTML = ''
  Object.keys(routes).forEach(k=> nav.appendChild(navLink(k, routes[k].title)))
}

function navigate(key){
  const route = routes[key] || routes.home
  document.getElementById('content').innerHTML = route.render()
  document.querySelectorAll('nav a').forEach(a=>a.classList.remove('active'))
  const el = document.getElementById('nav-'+key)
  if(el) el.classList.add('active')
  history.pushState({k}, route.title, '#'+key)
}

window.addEventListener('popstate', (e)=>{ const k = (e.state && e.state.k) || (location.hash && location.hash.slice(1)) || 'home'; navigate(k) })

buildNav()
const initial = (location.hash && location.hash.slice(1)) || 'home'
navigate(initial)

export { routes }
