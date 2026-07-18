import type { Locale } from "./i18n/translations";

const USERS_KEY = "sahaay_users";
const CURRENT_USER_KEY = "sahaay_current_user";
const FAMILY_KEY = "sahaay_family";
const ACTIVITIES_KEY = "sahaay_activities";
const WELLNESS_KEY = "sahaay_wellness";
const NOTIFICATIONS_KEY = "sahaay_notifications";

export interface StoredUser {
  id: string;
  email: string;
  password: string;
  fullName: string;
  role: "family_member" | "elder";
  locale: Locale;
}

export interface ElderProfile {
  id: string;
  displayName: string;
  sessionId: string;
  preferredLanguage: Locale;
  emergencyContact?: string;
}

export interface Family {
  id: string;
  name: string;
  inviteCode: string;
  elderProfiles: ElderProfile[];
}

export interface Activity {
  id: string;
  elderProfileId: string;
  activityType: string;
  title: string;
  description?: string;
  timestamp: number;
}

export interface WellnessCheck {
  id: string;
  elderProfileId: string;
  mood: string;
  appetite: string;
  sleepQuality: string;
  notes?: string;
  timestamp: number;
}

export interface LocalNotification {
  id: string;
  title: string;
  body: string;
  notificationType: "info" | "sos" | "reminder";
  isRead: boolean;
  elderProfileId?: string;
  timestamp: number;
}

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson<T>(key: string, value: T): void {
  localStorage.setItem(key, JSON.stringify(value));
}

function createId(): string {
  return crypto.randomUUID();
}

function createInviteCode(): string {
  return Math.random().toString(36).slice(2, 8).toUpperCase();
}

export function getUsers(): StoredUser[] {
  return readJson<StoredUser[]>(USERS_KEY, []);
}

export function saveUser(user: StoredUser): void {
  const users = getUsers().filter((item) => item.email !== user.email);
  users.push(user);
  writeJson(USERS_KEY, users);
}

export function findUser(email: string, password: string): StoredUser | null {
  return (
    getUsers().find(
      (user) =>
        user.email.toLowerCase() === email.toLowerCase() &&
        user.password === password,
    ) ?? null
  );
}

export function getCurrentUser(): StoredUser | null {
  return readJson<StoredUser | null>(CURRENT_USER_KEY, null);
}

export function setCurrentUser(user: StoredUser | null): void {
  if (user) {
    writeJson(CURRENT_USER_KEY, user);
  } else {
    localStorage.removeItem(CURRENT_USER_KEY);
  }
}

export function getFamily(): Family | null {
  return readJson<Family | null>(FAMILY_KEY, null);
}

export function saveFamily(family: Family): void {
  writeJson(FAMILY_KEY, family);
}

export function createFamily(name: string): Family {
  const family: Family = {
    id: createId(),
    name,
    inviteCode: createInviteCode(),
    elderProfiles: [],
  };
  saveFamily(family);
  return family;
}

export function joinFamily(inviteCode: string): Family | null {
  const existing = getFamily();
  if (existing && existing.inviteCode === inviteCode.toUpperCase()) {
    return existing;
  }
  const family: Family = {
    id: createId(),
    name: "Joined family",
    inviteCode: inviteCode.toUpperCase(),
    elderProfiles: [],
  };
  saveFamily(family);
  return family;
}

export function addElderProfile(
  displayName: string,
  sessionId: string,
  preferredLanguage: Locale = "en",
): ElderProfile {
  const family = getFamily() ?? createFamily("My family");
  const profile: ElderProfile = {
    id: createId(),
    displayName,
    sessionId,
    preferredLanguage,
  };
  family.elderProfiles.push(profile);
  saveFamily(family);
  return profile;
}

export function getElderProfile(id: string): ElderProfile | null {
  const family = getFamily();
  return family?.elderProfiles.find((profile) => profile.id === id) ?? null;
}

export function getActivities(): Activity[] {
  return readJson<Activity[]>(ACTIVITIES_KEY, []);
}

export function logActivity(
  elderProfileId: string,
  activityType: string,
  title: string,
  description?: string,
): Activity {
  const activity: Activity = {
    id: createId(),
    elderProfileId,
    activityType,
    title,
    description,
    timestamp: Date.now(),
  };
  const activities = [activity, ...getActivities()].slice(0, 200);
  writeJson(ACTIVITIES_KEY, activities);
  return activity;
}

export function getWellnessChecks(): WellnessCheck[] {
  return readJson<WellnessCheck[]>(WELLNESS_KEY, []);
}

export function saveWellnessCheck(
  check: Omit<WellnessCheck, "id" | "timestamp">,
): WellnessCheck {
  const record: WellnessCheck = {
    ...check,
    id: createId(),
    timestamp: Date.now(),
  };
  const checks = [record, ...getWellnessChecks()].slice(0, 100);
  writeJson(WELLNESS_KEY, checks);
  return record;
}

export function getNotifications(): LocalNotification[] {
  return readJson<LocalNotification[]>(NOTIFICATIONS_KEY, []);
}

export function addNotification(
  notification: Omit<LocalNotification, "id" | "timestamp" | "isRead">,
): LocalNotification {
  const record: LocalNotification = {
    ...notification,
    id: createId(),
    isRead: false,
    timestamp: Date.now(),
  };
  const items = [record, ...getNotifications()].slice(0, 50);
  writeJson(NOTIFICATIONS_KEY, items);
  return record;
}

export function markNotificationRead(id: string): void {
  const items = getNotifications().map((item) =>
    item.id === id ? { ...item, isRead: true } : item,
  );
  writeJson(NOTIFICATIONS_KEY, items);
}

export function getUnreadNotificationCount(): number {
  return getNotifications().filter((item) => !item.isRead).length;
}
