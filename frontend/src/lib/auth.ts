"use client";

import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth";

import { firebaseAuth } from "./firebase";

export type AuthenticatedUser = {
  id: string;
  firebase_uid: string;
  email: string | null;
  name: string | null;
  photo_url: string | null;
  session_id?: never;
};

export type AuthenticationResponse = {
  user: AuthenticatedUser;
  session: { id: string };
  token_type: "Bearer";
};

const googleProvider = new GoogleAuthProvider();

export async function signInWithGoogle(): Promise<AuthenticationResponse> {
  const credential = await signInWithPopup(firebaseAuth, googleProvider);
  const idToken = await credential.user.getIdToken();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    await firebaseSignOut(firebaseAuth);
    throw new Error("NEXT_PUBLIC_API_URL is not configured");
  }

  const response = await fetch(`${apiUrl.replace(/\/$/, "")}/api/v1/auth/firebase`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });

  if (!response.ok) {
    await firebaseSignOut(firebaseAuth);
    const payload = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;
    throw new Error(payload?.detail ?? "Authentication failed");
  }

  return (await response.json()) as AuthenticationResponse;
}

export async function getFirebaseIdToken(): Promise<string> {
  const user = firebaseAuth.currentUser;
  if (!user) {
    throw new Error("User is not signed in");
  }
  return user.getIdToken();
}

export async function signOut(): Promise<void> {
  await firebaseSignOut(firebaseAuth);
}
