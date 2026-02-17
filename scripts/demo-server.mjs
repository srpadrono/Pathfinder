#!/usr/bin/env node
import http from 'node:http';

const port = Number(process.env.PORT || 3000);

const html = (body) => `<!doctype html><html><head><meta charset="utf-8"><title>Pathfinder Demo</title></head><body>${body}</body></html>`;

function send(res, status, contentType, body) {
  res.writeHead(status, { 'content-type': contentType });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url || '/', `http://${req.headers.host}`);

  if (req.method === 'GET' && url.pathname === '/health') {
    return send(res, 200, 'application/json', JSON.stringify({ ok: true }));
  }

  if (req.method === 'GET' && url.pathname === '/auth/login') {
    return send(
      res,
      200,
      'text/html; charset=utf-8',
      html(`
        <h1>Login</h1>
        <form id="login-form">
          <input id="email" type="email" name="email" inputmode="email" required />
          <input id="password" type="password" name="password" style="display:none" required />
          <button type="submit">Submit</button>
        </form>
        <script>
          const form = document.getElementById('login-form');
          const email = document.getElementById('email');
          const password = document.getElementById('password');
          let phase = 'email';
          form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (phase === 'email') {
              phase = 'password';
              password.style.display = 'inline-block';
              password.focus();
              return;
            }
            localStorage.setItem('auth', JSON.stringify({ email: email.value, at: Date.now() }));
            window.location.href = '/example';
          });
        </script>
      `)
    );
  }

  if (req.method === 'GET' && url.pathname === '/api/data') {
    return send(res, 200, 'application/json', JSON.stringify([{ id: 1, name: 'demo' }]));
  }

  if (req.method === 'GET' && url.pathname === '/example') {
    return send(
      res,
      200,
      'text/html; charset=utf-8',
      html(`
        <h1>Example Page</h1>
        <button data-action="submit">Submit</button>
        <div id="out"></div>
        <script>
          const out = document.getElementById('out');
          fetch('/api/data')
            .then(async (r) => {
              if (!r.ok) throw new Error('api error');
              const data = await r.json();
              if (!Array.isArray(data) || data.length === 0) {
                out.innerHTML = '<div data-empty>No data available</div>';
              }
            })
            .catch(() => {
              out.innerHTML = '<div data-error>Something went wrong</div>';
            });

          document.querySelector('button[data-action="submit"]').addEventListener('click', () => {
            out.innerHTML += '<div data-result>Action complete</div>';
          });
        </script>
      `)
    );
  }

  return send(res, 404, 'text/plain; charset=utf-8', 'Not found');
});

server.listen(port, '0.0.0.0', () => {
  console.log(`Pathfinder demo server running on http://0.0.0.0:${port}`);
});
