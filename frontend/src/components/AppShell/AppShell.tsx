"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { localeLabels, type Locale } from "@/lib/i18n/translations";
import styles from "./AppShell.module.css";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { locale, setLocale, tr } = useI18n();

  const links = [
    { href: "/", label: tr("navHome") },
    { href: "/elder", label: tr("navElder") },
    { href: "/family", label: tr("navFamily") },
    { href: "/elder/calendar", label: tr("navCalendar") },
  ];

  return (
    <div className={styles.shell}>
      <header className={styles.nav}>
        <Link href="/" className={styles.brand}>
          <span className={styles.logo} aria-hidden="true">
            🙏
          </span>
          <span className={styles.brandText}>
            <span className={styles.brandName}>{tr("appName")}</span>
            <span className={styles.brandTagline}>{tr("tagline")}</span>
          </span>
        </Link>

        {user ? (
          <nav className={styles.links} aria-label="Main">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`${styles.link} ${pathname === link.href ? styles.active : ""}`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        ) : (
          <nav className={styles.links} aria-label="Main">
            <Link
              href="/login"
              className={`${styles.link} ${pathname === "/login" ? styles.active : ""}`}
            >
              {tr("navLogin")}
            </Link>
            <Link
              href="/register"
              className={`${styles.link} ${pathname === "/register" ? styles.active : ""}`}
            >
              {tr("navRegister")}
            </Link>
          </nav>
        )}

        {user ? (
          <div className={styles.actions}>
            <select
              className={styles.langSelect}
              value={locale}
              onChange={(event) => setLocale(event.target.value as Locale)}
              aria-label="Language"
            >
              {(Object.keys(localeLabels) as Locale[]).map((key) => (
                <option key={key} value={key}>
                  {localeLabels[key]}
                </option>
              ))}
            </select>

            <button type="button" className={styles.logout} onClick={logout}>
              {tr("navLogout")}
            </button>
          </div>
        ) : null}
      </header>
      <main className={styles.main}>{children}</main>
    </div>
  );
}
