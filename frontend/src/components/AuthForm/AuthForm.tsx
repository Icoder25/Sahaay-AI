"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import styles from "./AuthForm.module.css";

interface AuthFormProps {
  mode: "login" | "register";
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const { login, register } = useAuth();
  const { tr, locale } = useI18n();
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const form = new FormData(event.currentTarget);

    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");

    if (mode === "login") {
      const ok = login(email, password);
      if (!ok) {
        setError("Invalid email or password.");
        return;
      }
      router.push("/family");
      return;
    }

    const fullName = String(form.get("fullName") ?? "");
    const role = String(form.get("role") ?? "family_member") as
      | "family_member"
      | "elder";
    const familyName = String(form.get("familyName") ?? "");
    const inviteCode = String(form.get("inviteCode") ?? "");

    if (!fullName || !email || password.length < 6) {
      setError("Please fill all fields. Password must be at least 6 characters.");
      return;
    }

    register({
      email,
      password,
      fullName,
      role,
      locale,
      familyName: familyName || undefined,
      inviteCode: inviteCode || undefined,
    });

    router.push(role === "elder" ? "/elder" : "/family");
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>
          {mode === "login" ? tr("loginTitle") : tr("registerTitle")}
        </h1>

        <form className={styles.form} onSubmit={handleSubmit}>
          {mode === "register" ? (
            <>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="fullName">
                  {tr("fullName")}
                </label>
                <input
                  id="fullName"
                  name="fullName"
                  className={styles.input}
                  required
                />
              </div>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="role">
                  {tr("role")}
                </label>
                <select id="role" name="role" className={styles.select} defaultValue="family_member">
                  <option value="family_member">{tr("roleFamily")}</option>
                  <option value="elder">{tr("roleElder")}</option>
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="familyName">
                  {tr("familyName")}
                </label>
                <input id="familyName" name="familyName" className={styles.input} />
              </div>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="inviteCode">
                  {tr("inviteCode")}
                </label>
                <input id="inviteCode" name="inviteCode" className={styles.input} />
              </div>
            </>
          ) : null}

          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">
              {tr("email")}
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className={styles.input}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">
              {tr("password")}
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className={styles.input}
              minLength={6}
              required
            />
          </div>

          {error ? <p className={styles.error}>{error}</p> : null}

          <button type="submit" className={styles.submit}>
            {tr("submit")}
          </button>
        </form>

        <p className={styles.footer}>
          {mode === "login" ? tr("noAccount") : tr("hasAccount")}{" "}
          <Link href={mode === "login" ? "/register" : "/login"}>
            {mode === "login" ? tr("navRegister") : tr("navLogin")}
          </Link>
        </p>
      </div>
    </div>
  );
}
