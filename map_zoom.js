/**
 * SVG map zoom / pan / fullscreen / reset interactions
 * - Mouse wheel zoom (anchor at cursor)
 * - Double-click on empty area zoom in
 * - Two-finger pinch zoom on touch devices
 * - Drag to pan when zoomed in
 * - Fullscreen toggle button
 * - Reset button to restore initial view
 * - Map pins, route labels and dashed lines keep visual size while zooming
 */
(function(){
  'use strict';

  const MIN_SCALE = 1;
  const MAX_SCALE = 6;
  const WHEEL_FACTOR = 1.18;
  const DOUBLE_TAP_FACTOR = 1.6;

  function init(svg){
    const W = 780, H = 470;
    let scale = 1;
    let cx = W / 2, cy = H / 2;
    let dragging = false;
    let lastX, lastY;
    let pinch = null;
    let startDist = 0;
    const pins = Array.from(svg.querySelectorAll('.pin-fixed'));
    const legs = Array.from(svg.querySelectorAll('.leg-fixed'));

    function reset(){
      scale = 1;
      cx = W / 2;
      cy = H / 2;
      setViewBox();
    }

    function setViewBox(){
      const vw = W / scale;
      const vh = H / scale;
      const vx = cx - vw / 2;
      const vy = cy - vh / 2;
      svg.setAttribute('viewBox', `${vx.toFixed(2)} ${vy.toFixed(2)} ${vw.toFixed(2)} ${vh.toFixed(2)}`);
      // Only capture touch gestures (block page scroll) while actually zoomed in.
      svg.style.touchAction = scale > 1 ? 'none' : 'pan-y';
      updateFixedElements();
    }

    function updateFixedElements(){
      // Keep pins visually the same size while the map zooms.
      const inv = 1 / scale;
      pins.forEach(function(pin){
        const pcx = parseFloat(pin.getAttribute('data-cx') || 0);
        const pcy = parseFloat(pin.getAttribute('data-cy') || 0);
        pin.setAttribute('transform', `translate(${pcx}, ${pcy}) scale(${inv}) translate(${-pcx}, ${-pcy})`);
      });
      // Keep leg labels visually the same size and centered on their rect.
      legs.forEach(function(leg){
        const rect = leg.querySelector('rect');
        if (!rect) return;
        const rx = parseFloat(rect.getAttribute('x') || 0);
        const ry = parseFloat(rect.getAttribute('y') || 0);
        const rw = parseFloat(rect.getAttribute('width') || 0);
        const rh = parseFloat(rect.getAttribute('height') || 0);
        const lx = rx + rw / 2;
        const ly = ry + rh / 2;
        leg.setAttribute('transform', `translate(${lx}, ${ly}) scale(${inv}) translate(${-lx}, ${-ly})`);
      });
      // Dashed routes keep a constant on-screen width AND dash spacing at every zoom via
      // CSS `.route-line { vector-effect: non-scaling-stroke }` — no per-zoom recompute.
      // (An earlier JS rescale here fought the CSS and thinned the dots when zoomed in.)
    }

    function clampScale(s){
      return Math.min(MAX_SCALE, Math.max(MIN_SCALE, s));
    }

    function clientToSvgXY(clientX, clientY){
      const rect = svg.getBoundingClientRect();
      return {
        x: (clientX - rect.left) * (W / rect.width),
        y: (clientY - rect.top) * (H / rect.height)
      };
    }

    function zoomAt(clientX, clientY, factor){
      const p = clientToSvgXY(clientX, clientY);
      const wx = cx + (p.x - W / 2) / scale;
      const wy = cy + (p.y - H / 2) / scale;
      const newScale = clampScale(scale * factor);
      if (newScale === scale) return;
      cx = wx - (p.x - W / 2) / newScale;
      cy = wy - (p.y - H / 2) / newScale;
      scale = newScale;
      setViewBox();
    }

    function pan(dx, dy){
      if (scale <= 1) return;
      const rect = svg.getBoundingClientRect();
      cx -= dx * (W / rect.width) / scale;
      cy -= dy * (H / rect.height) / scale;
      setViewBox();
    }

    svg.addEventListener('wheel', function(e){
      // Plain wheel scrolls the page; Ctrl/⌘ + wheel zooms the map (avoids scroll-trapping
      // on a long page that stacks several maps). Pinch, double-click and ⛶ still zoom directly.
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const factor = e.deltaY < 0 ? WHEEL_FACTOR : 1 / WHEEL_FACTOR;
      zoomAt(e.clientX, e.clientY, factor);
    }, { passive: false });

    svg.addEventListener('dblclick', function(e){
      if (e.target.closest && e.target.closest('a')) return;
      e.preventDefault();
      zoomAt(e.clientX, e.clientY, DOUBLE_TAP_FACTOR);
    });

    svg.addEventListener('mousedown', function(e){
      if (e.button !== 0) return;
      if (scale <= 1) return;
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      svg.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', function(e){
      if (!dragging) return;
      pan(e.clientX - lastX, e.clientY - lastY);
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener('mouseup', function(){
      dragging = false;
      svg.style.cursor = '';
    });

    svg.addEventListener('touchstart', function(e){
      if (e.touches.length === 2){
        const t1 = e.touches[0], t2 = e.touches[1];
        pinch = {
          cx: (t1.clientX + t2.clientX) / 2,
          cy: (t1.clientY + t2.clientY) / 2
        };
        startDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
      } else if (e.touches.length === 1 && scale > 1){
        dragging = true;
        lastX = e.touches[0].clientX;
        lastY = e.touches[0].clientY;
      }
    }, { passive: false });

    svg.addEventListener('touchmove', function(e){
      if (e.touches.length === 2 && pinch){
        e.preventDefault();
        const t1 = e.touches[0], t2 = e.touches[1];
        const dist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
        const centerX = (t1.clientX + t2.clientX) / 2;
        const centerY = (t1.clientY + t2.clientY) / 2;
        if (startDist > 0){
          zoomAt(centerX, centerY, dist / startDist);
          startDist = dist;
          pinch.cx = centerX;
          pinch.cy = centerY;
        }
      } else if (e.touches.length === 1 && dragging){
        e.preventDefault();
        const t = e.touches[0];
        pan(t.clientX - lastX, t.clientY - lastY);
        lastX = t.clientX;
        lastY = t.clientY;
      }
    }, { passive: false });

    svg.addEventListener('touchend', function(e){
      if (e.touches.length < 2) pinch = null;
      if (e.touches.length === 0) dragging = false;
    });

    return { reset: reset };
  }

  function initFullscreen(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      if (document.fullscreenElement){
        if (document.exitFullscreen) document.exitFullscreen();
      } else {
        const card = btn.closest('.daycard');
        if (!card) return;
        if (card.requestFullscreen) card.requestFullscreen();
        else if (card.webkitRequestFullscreen) card.webkitRequestFullscreen();
      }
    });
  }

  const controls = {};
  document.querySelectorAll('svg.map').forEach(function(svg){
    const dayId = svg.closest('.daycard').id;
    controls[dayId] = init(svg);
  });
  document.querySelectorAll('.map-fs').forEach(initFullscreen);
  document.querySelectorAll('.map-reset').forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      const dayId = btn.getAttribute('data-target');
      if (controls[dayId]) controls[dayId].reset();
    });
  });
})();
