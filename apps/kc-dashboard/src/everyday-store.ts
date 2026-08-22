import { useSyncExternalStore } from "react";
import {
  DEFAULT_PILOT,
  DEFAULT_PROFILE,
  PILOT_STORAGE_KEY,
  PROFILE_STORAGE_KEY,
  parsePilot,
  parseProfile,
  serializePilot,
  serializeProfile,
  type InteractionProfile,
  type PilotState,
} from "./everyday-model";

type Listener = () => void;

let profileSnapshot: InteractionProfile = { ...DEFAULT_PROFILE };
let pilotSnapshot: PilotState = { ...DEFAULT_PILOT };
let profileHydrated = false;
let pilotHydrated = false;
let storageListenerInstalled = false;

const profileListeners = new Set<Listener>();
const pilotListeners = new Set<Listener>();

function emit(listeners: Set<Listener>) {
  listeners.forEach((listener) => listener());
}

function safeStorage() {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function installStorageListener() {
  if (typeof window === "undefined" || storageListenerInstalled) return;
  storageListenerInstalled = true;
  window.addEventListener("storage", (event) => {
    if (event.key === PROFILE_STORAGE_KEY) {
      profileSnapshot = parseProfile(event.newValue);
      profileHydrated = true;
      emit(profileListeners);
    }
    if (event.key === PILOT_STORAGE_KEY) {
      pilotSnapshot = parsePilot(event.newValue);
      pilotHydrated = true;
      emit(pilotListeners);
    }
  });
}

function hydrateProfile() {
  if (profileHydrated) return;
  profileHydrated = true;
  installStorageListener();
  profileSnapshot = parseProfile(safeStorage()?.getItem(PROFILE_STORAGE_KEY));
}

function hydratePilot() {
  if (pilotHydrated) return;
  pilotHydrated = true;
  installStorageListener();
  pilotSnapshot = parsePilot(safeStorage()?.getItem(PILOT_STORAGE_KEY));
}

function getProfileSnapshot() {
  hydrateProfile();
  return profileSnapshot;
}

function getPilotSnapshot() {
  hydratePilot();
  return pilotSnapshot;
}

export function setInteractionProfile(next: InteractionProfile) {
  profileSnapshot = parseProfile(serializeProfile(next));
  profileHydrated = true;
  safeStorage()?.setItem(PROFILE_STORAGE_KEY, serializeProfile(profileSnapshot));
  emit(profileListeners);
}

export function patchInteractionProfile(patch: Partial<InteractionProfile>) {
  setInteractionProfile({ ...getProfileSnapshot(), ...patch });
}

export function resetInteractionProfile() {
  // Deliberately touches only the profile key. Pilot progress is a separate
  // local state domain so preference reset cannot corrupt workflow progress.
  profileSnapshot = { ...DEFAULT_PROFILE };
  profileHydrated = true;
  safeStorage()?.setItem(PROFILE_STORAGE_KEY, serializeProfile(profileSnapshot));
  emit(profileListeners);
}

export function setPilotProgress(next: PilotState) {
  pilotSnapshot = parsePilot(serializePilot(next));
  pilotHydrated = true;
  safeStorage()?.setItem(PILOT_STORAGE_KEY, serializePilot(pilotSnapshot));
  emit(pilotListeners);
}

export function resetPilotProgress() {
  pilotSnapshot = { ...DEFAULT_PILOT };
  pilotHydrated = true;
  safeStorage()?.setItem(PILOT_STORAGE_KEY, serializePilot(pilotSnapshot));
  emit(pilotListeners);
}

function subscribeProfile(listener: Listener) {
  profileListeners.add(listener);
  return () => profileListeners.delete(listener);
}

function subscribePilot(listener: Listener) {
  pilotListeners.add(listener);
  return () => pilotListeners.delete(listener);
}

export function useInteractionProfile() {
  return useSyncExternalStore(
    subscribeProfile,
    getProfileSnapshot,
    () => DEFAULT_PROFILE,
  );
}

export function usePilotProgress() {
  return useSyncExternalStore(
    subscribePilot,
    getPilotSnapshot,
    () => DEFAULT_PILOT,
  );
}

function subscribeConnectivity(listener: Listener) {
  if (typeof window === "undefined") return () => undefined;
  window.addEventListener("online", listener);
  window.addEventListener("offline", listener);
  return () => {
    window.removeEventListener("online", listener);
    window.removeEventListener("offline", listener);
  };
}

function onlineSnapshot() {
  return typeof navigator === "undefined" ? true : navigator.onLine;
}

export function useOnlineStatus() {
  return useSyncExternalStore(subscribeConnectivity, onlineSnapshot, () => true);
}
