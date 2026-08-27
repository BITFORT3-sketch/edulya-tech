// EDULYA-TECH — script.js
//
// Ce fichier appelle le vrai backend Flask (voir js/config.js pour l'URL).
// Toutes les requêtes liées à un compte utilisent { credentials: 'include' }
// pour envoyer/recevoir le cookie de session.
const API_URL= 'https://edulya-tech.onrender.com';
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('navToggle');
  const nav = document.getElementById('mainNav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('nav-open');
      toggle.classList.toggle('is-open');
    });
  }

  // ----- Actions du header (Connexion/Inscription, etc.) dans le menu mobile -----
  // Sur téléphone, le menu hamburger n'affichait que les liens Accueil/
  // Formations/À propos/Contacts : les actions à droite du header restaient
  // invisibles (display:none). On les déplace physiquement dans le menu
  // mobile pour qu'elles y soient accessibles, et on les remet à leur place
  // d'origine dès qu'on repasse en affichage bureau.
  const headerActions = document.querySelector('.header-actions');
  if (headerActions && nav) {
    const originalParent = headerActions.parentElement;
    const originalNextSibling = headerActions.nextSibling;
    const mobileQuery = window.matchMedia('(max-width: 680px)');

    const placeHeaderActions = () => {
      if (mobileQuery.matches) {
        nav.appendChild(headerActions);
      } else if (headerActions.parentElement !== originalParent) {
        originalParent.insertBefore(headerActions, originalNextSibling);
      }
    };

    placeHeaderActions();
    mobileQuery.addEventListener('change', placeHeaderActions);
  }

  // ----- Lien "Connexion / Inscription" → "Tableau de bord" si déjà connecté -----
  // S'applique sur toutes les pages publiques : tant que l'utilisateur ne
  // s'est pas explicitement déconnecté, il retrouve un accès rapide à son
  // tableau de bord au lieu de revoir "Connexion / Inscription".
  const authLink = document.getElementById('authLink');
  if (authLink) {
    fetch(`${API_URL}/api/me`, { credentials: 'include' })
      .then((res) => res.json())
      .then(({ user }) => {
        if (user) {
          authLink.textContent = '← Retour au tableau de bord';
          authLink.href = 'tableau-de-bord.html';
        }
      })
      .catch(() => { /* pas connecté ou backend injoignable : on garde le lien par défaut */ });
  }

  // ----- Thème clair / sombre -----
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      if (isLight) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('edulya_theme', 'dark');
      } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('edulya_theme', 'light');
      }
    });
  }

  // ----- Afficher / masquer le mot de passe -----
  document.querySelectorAll('.toggle-password').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';
      btn.classList.toggle('is-visible', !showing);
      btn.setAttribute('aria-label', showing ? 'Afficher le mot de passe' : 'Masquer le mot de passe');
    });
  });

  // ----- Formulaire de contact -----
  const contactForm = document.getElementById('contactForm');
  const formNote = document.getElementById('formNote');

  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      formNote.textContent = 'Envoi en cours...';

      const body = {
        nom: document.getElementById('nom').value,
        email: document.getElementById('email').value,
        sujet: document.getElementById('sujet').value,
        message: document.getElementById('message').value,
      };

      try {
        const res = await fetch(`${API_URL}/api/contact`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) {
          formNote.textContent = data.error || 'Une erreur est survenue.';
          return;
        }
        formNote.textContent = 'Message envoyé — nous te répondrons sous 24 à 48h.';
        contactForm.reset();
      } catch (err) {
        formNote.textContent = 'Impossible de contacter le serveur. Vérifie qu\'il est bien lancé.';
      }
    });
  }

  // ----- Mot de passe oublié -----
  const forgotForm = document.getElementById('forgotForm');
  const forgotNote = document.getElementById('forgotNote');
  if (forgotForm) {
    forgotForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      forgotNote.textContent = 'Envoi en cours...';
      const email = document.getElementById('forgotEmail').value;

      try {
        await fetch(`${API_URL}/api/mot-de-passe-oublie`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });
        forgotNote.textContent = 'Si un compte existe avec cet email, un lien de réinitialisation vient d\'être envoyé.';
        forgotForm.reset();
      } catch (err) {
        forgotNote.textContent = 'Impossible de contacter le serveur. Vérifie qu\'il est bien lancé.';
      }
    });
  }

  // ----- Réinitialisation du mot de passe -----
  const resetForm = document.getElementById('resetForm');
  const resetNote = document.getElementById('resetNote');
  if (resetForm) {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    resetForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!token) {
        resetNote.textContent = 'Lien invalide — redemande un email de réinitialisation.';
        return;
      }

      const password = document.getElementById('newPassword').value;
      const confirm = document.getElementById('confirmPassword').value;
      if (password !== confirm) {
        resetNote.textContent = 'Les deux mots de passe ne correspondent pas.';
        return;
      }

      resetNote.textContent = 'Modification en cours...';
      try {
        const res = await fetch(`${API_URL}/api/reinitialiser-mot-de-passe`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token, password }),
        });
        const data = await res.json();

        if (!res.ok) {
          resetNote.textContent = data.error || 'Une erreur est survenue.';
          return;
        }
        resetNote.textContent = 'Mot de passe modifié — redirection vers la connexion...';
        setTimeout(() => { window.location.href = 'connexion.html'; }, 1200);
      } catch (err) {
        resetNote.textContent = 'Impossible de contacter le serveur. Vérifie qu\'il est bien lancé.';
      }
    });
  }

  // ----- Connexion -----
  const loginForm = document.getElementById('loginForm');
  const loginNote = document.getElementById('loginNote');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      loginNote.textContent = 'Connexion en cours...';

      const body = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value,
      };

      try {
        const res = await fetch(`${API_URL}/api/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) {
          loginNote.textContent = data.error || 'Email ou mot de passe incorrect.';
          return;
        }
        loginNote.textContent = 'Connexion réussie — redirection...';
        window.location.href = 'tableau-de-bord.html';
      } catch (err) {
        loginNote.textContent = 'Impossible de contacter le serveur. Vérifie qu\'il est bien lancé.';
      }
    });
  }

  // ----- Inscription -----
  const signupForm = document.getElementById('signupForm');
  const signupNote = document.getElementById('signupNote');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      signupNote.textContent = 'Création du compte...';

      const body = {
        nom: document.getElementById('nom').value,
        prenom: document.getElementById('prenom').value,
        email: document.getElementById('signupEmail').value,
        telephone: document.getElementById('telephone').value,
        password: document.getElementById('signupPassword').value,
      };

      try {
        const res = await fetch(`${API_URL}/api/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) {
          signupNote.textContent = data.error || 'Une erreur est survenue.';
          return;
        }
        signupNote.textContent = 'Compte créé — redirection...';
        window.location.href = 'tableau-de-bord.html';
      } catch (err) {
        signupNote.textContent = 'Impossible de contacter le serveur. Vérifie qu\'il est bien lancé.';
      }
    });
  }

  // ----- Achat de formation (sur le tableau de bord) -----
  document.querySelectorAll('.buy-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const formationId = btn.dataset.formationId;
      const originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = '...';

      try {
        const res = await fetch(`${API_URL}/api/achats`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ formation_id: formationId }),
        });

        if (res.status === 401) {
          window.location.href = 'connexion.html';
          return;
        }
        if (!res.ok) {
          btn.textContent = originalText;
          btn.disabled = false;
          return;
        }
        btn.textContent = 'Acheté ✓';
        chargerMesFormations();
      } catch (err) {
        btn.textContent = originalText;
        btn.disabled = false;
      }
    });
  });

  // ----- Page détail d'une formation (récupérée depuis l'API) -----
  const formationTitleEl = document.getElementById('formationTitle');
  if (formationTitleEl) {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    (async () => {
      let data;
      try {
        const res = await fetch(`${API_URL}/api/formations/${id}`);
        if (!res.ok) throw new Error('not found');
        const body = await res.json();
        data = body.formation;
      } catch (err) {
        document.querySelector('.formation-intro').style.display = 'none';
        document.querySelector('.formations').style.display = 'none';
        document.getElementById('notFound').style.display = 'block';
        return;
      }

      // À partir d'ici, la formation existe : on affiche ses infos.
      // Chaque champ est protégé (valeur par défaut) pour ne jamais faire planter la page.
      document.getElementById('breadcrumbCurrent').textContent = data.titre || '';
      document.getElementById('formationTag').textContent = `// ${(data.titre || '').toLowerCase()}`;
      formationTitleEl.textContent = data.titre || '';
      document.getElementById('formationTagline').textContent = data.tagline || '';
      document.getElementById('formationNiveau').textContent = `Niveau : ${data.niveau || '—'}`;
      document.getElementById('formationDuree').textContent = `Durée : ${data.duree || '—'}`;
      const prixNombre = Number(data.prix) || 0;
      document.getElementById('formationPrix').textContent = `${prixNombre.toLocaleString('fr-FR')} FCFA`;
      document.getElementById('formationDescription').textContent = data.description || '';

      const img = document.getElementById('formationImg');
      if (img) {
        img.src = data.image || '';
        img.alt = `Formation ${data.titre || ''}`;
      }

      // Programme du cours (informatif, public — le contenu détaillé reste
      // réservé aux acheteurs sur formation-cours.html).
      const programmeEl = document.getElementById('formationProgramme');
      if (programmeEl && Array.isArray(data.programme)) {
        programmeEl.innerHTML = data.programme.map((item, i) => `
          <div class="programme-item">
            <span class="valeur-num">${String(i + 1).padStart(2, '0')}</span>
            <p>${item}</p>
          </div>
        `).join('');
      }

      const cta = document.getElementById('formationCta');
      const accessNote = document.getElementById('formationAccessNote');

      // On vérifie si l'utilisateur est connecté et a déjà acheté cette formation,
      // pour lui proposer directement d'accéder au cours plutôt que "S'inscrire".
      try {
        const meRes = await fetch(`${API_URL}/api/me`, { credentials: 'include' });
        const { user } = await meRes.json();

        if (user) {
          const achatsRes = await fetch(`${API_URL}/api/mes-achats`, { credentials: 'include' });
          const { achats } = await achatsRes.json();
          const possede = (achats || []).find((a) => a.formation && a.formation.id === id);

          if (possede) {
            cta.href = `formation-cours.html?id=${id}`;
            cta.textContent = 'Accéder au cours';
            accessNote.textContent = 'Tu as déjà accès à cette formation.';
          } else {
            cta.href = 'tableau-de-bord.html#acheter';
            cta.textContent = "Acheter cette formation";
          }
        } else {
          cta.href = 'connexion.html';
          cta.textContent = 'Se connecter pour acheter';
        }
      } catch (err) {
        // Si la vérification échoue (ex: backend non lancé), on garde le CTA par défaut.
        cta.href = 'inscription.html';
      }
    })();
  }

  // ----- Page contenu du cours (protégée — nécessite d'avoir acheté la formation) -----
  const courseTitleEl = document.getElementById('courseTitle');
  if (courseTitleEl) {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    (async () => {
      const denyAccess = () => {
        document.querySelector('.page-intro').style.display = 'none';
        document.querySelector('.formations').style.display = 'none';
        document.getElementById('accessDenied').style.display = 'block';
      };

      try {
        const meRes = await fetch(`${API_URL}/api/me`, { credentials: 'include' });
        const { user } = await meRes.json();
        if (!user) { window.location.href = 'connexion.html'; return; }

        const achatsRes = await fetch(`${API_URL}/api/mes-achats`, { credentials: 'include' });
        const { achats } = await achatsRes.json();
        const possede = (achats || []).find((a) => a.formation && a.formation.id === id);

        if (!possede) { denyAccess(); return; }

        const formRes = await fetch(`${API_URL}/api/formations/${id}`);
        const { formation: data } = await formRes.json();

        document.getElementById('courseTag').textContent = `// ${data.titre.toLowerCase()}`;
        courseTitleEl.textContent = data.titre;
        document.getElementById('courseTagline').textContent = data.tagline || '';
        document.getElementById('courseDescription').textContent = data.description || '';

        const programmeEl = document.getElementById('courseProgramme');
        const modules = Array.isArray(data.programme) ? data.programme : [];
        programmeEl.innerHTML = modules.map((item, i) => `
          <div class="programme-item">
            <span class="valeur-num">✓ ${String(i + 1).padStart(2, '0')}</span>
            <p>${item}</p>
          </div>
        `).join('');

        const downloadBtn = document.getElementById('downloadBtn');
        // Le bouton pointe vers la route backend protégée (elle vérifie à
        // nouveau l'achat côté serveur avant de rediriger vers le vrai PDF) —
        // jamais directement vers le lien Drive, qui n'est plus renvoyé par l'API.
        downloadBtn.href = `${API_URL}/api/formations/${id}/telecharger`;

        // ----- Avis sur la formation (réservé aux acheteurs, comme le reste de la page) -----
        const avisListe = document.getElementById('avisListe');
        const avisForm = document.getElementById('avisForm');
        const avisNote = document.getElementById('avisNote');

        // Les avis viennent des utilisateurs (contrairement au contenu des
        // formations) — on échappe donc le HTML avant de l'insérer, pour
        // éviter qu'un message contenant des balises ne s'exécute.
        const echapperHtml = (texte) => {
          const div = document.createElement('div');
          div.textContent = texte;
          return div.innerHTML;
        };

        const rendreAvis = (liste) => {
          if (!liste.length) {
            avisListe.innerHTML = '<p class="page-intro-sub">Aucun avis pour le moment — sois le premier à en laisser un.</p>';
            return;
          }
          avisListe.innerHTML = liste.map((a) => `
            <div class="avis-item ${a.user_id === user.id ? 'avis-mine' : ''}">
              <div class="avis-item-head">
                <span class="avis-item-auteur">${a.user_id === user.id ? 'Toi' : echapperHtml(a.auteur)}</span>
                <span>${new Date(a.date_envoi).toLocaleDateString('fr-FR')}</span>
              </div>
              <p>${echapperHtml(a.message)}</p>
            </div>
          `).join('');
          avisListe.scrollTop = avisListe.scrollHeight;
        };

        const chargerAvis = async () => {
          try {
            const res = await fetch(`${API_URL}/api/formations/${id}/avis`, { credentials: 'include' });
            const data = await res.json();
            rendreAvis(data.avis || []);
          } catch (err) {
            avisListe.innerHTML = '<p class="page-intro-sub">Impossible de charger les avis pour le moment.</p>';
          }
        };

        chargerAvis();

        if (avisForm) {
          avisForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const textarea = document.getElementById('avisMessage');
            const message = textarea.value.trim();
            if (!message) return;

            avisNote.textContent = 'Envoi en cours...';
            try {
              const res = await fetch(`${API_URL}/api/formations/${id}/avis`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ message }),
              });
              const data = await res.json();

              if (!res.ok) {
                avisNote.textContent = data.error || 'Une erreur est survenue.';
                return;
              }
              textarea.value = '';
              avisNote.textContent = '';
              chargerAvis();
            } catch (err) {
              avisNote.textContent = 'Impossible de contacter le serveur.';
            }
          });
        }
      } catch (err) {
        denyAccess();
      }
    })();
  }

  // ----- Tableau de bord -----
  const welcomeTitle = document.getElementById('welcomeTitle');
  if (welcomeTitle) {
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/me`, { credentials: 'include' });
        const { user } = await res.json();

        if (!user) {
          window.location.href = 'connexion.html';
          return;
        }

        welcomeTitle.textContent = `Bonjour ${user.prenom} 👋`;
        const greeting = document.getElementById('userGreeting');
        if (greeting) greeting.textContent = user.email;

        const setText = (elId, value) => {
          const el = document.getElementById(elId);
          if (el) el.textContent = value || '—';
        };
        setText('profNom', user.nom);
        setText('profPrenom', user.prenom);
        setText('profEmail', user.email);
        setText('profTel', user.telephone);

        chargerMesFormations();
      } catch (err) {
        window.location.href = 'connexion.html';
      }
    })();
  }

  // ----- Déconnexion -----
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await fetch(`${API_URL}/api/logout`, { method: 'POST', credentials: 'include' });
      } finally {
        window.location.href = 'index.html';
      }
    });
  }
});

// Récupère les formations déjà achetées, les affiche dans "Mes formations"
// avec un lien de téléchargement, ET met à jour les boutons "Acheter" du
// catalogue pour qu'ils affichent déjà "Acheté ✓" sans avoir besoin de recliquer.
async function chargerMesFormations() {
  const container = document.getElementById('myFormationsEmpty');

  try {
    const res = await fetch(`${API_URL}/api/mes-achats`, { credentials: 'include' });
    if (!res.ok) return;
    const { achats } = await res.json();

    if (!achats || achats.length === 0) return;

    // Met à jour "Mes formations" avec un lien vers le contenu du cours pour chacune.
    if (container) {
      container.innerHTML = achats.map((a) => {
        const lien = `<a href="formation-cours.html?id=${a.formation.id}" class="btn btn-outline btn-sm">Voir le cours</a>`;
        return `
          <div class="profile-list" style="text-align:left;">
            <div><dt>${a.formation.titre}</dt><dd>${lien}</dd></div>
          </div>
        `;
      }).join('');
    }

    // Marque chaque bouton "Acheter" déjà possédé comme "Acheté ✓" (désactivé).
    const idsPossedes = new Set(achats.map((a) => a.formation && a.formation.id));
    document.querySelectorAll('.buy-btn').forEach((btn) => {
      if (idsPossedes.has(btn.dataset.formationId)) {
        btn.textContent = 'Acheté ✓';
        btn.disabled = true;
      }
    });
  } catch (err) {
    // silencieux : l'état vide par défaut reste affiché
  }
}
