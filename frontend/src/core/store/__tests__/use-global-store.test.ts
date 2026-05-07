import { describe, it, expect, beforeEach } from 'vitest';
import { useGlobalStore } from '../use-global-store';

describe('useGlobalStore', () => {
  beforeEach(() => {
    useGlobalStore.getState().clearSession();
    useGlobalStore.getState().setSettingsOpen(false);
  });

  it('should have initial state', () => {
    const state = useGlobalStore.getState();
    expect(state.isSettingsOpen).toBe(false);
    expect(state.user.id).toBe(null);
  });

  it('should toggle settings drawer', () => {
    useGlobalStore.getState().setSettingsOpen(true);
    expect(useGlobalStore.getState().isSettingsOpen).toBe(true);
    
    useGlobalStore.getState().setSettingsOpen(false);
    expect(useGlobalStore.getState().isSettingsOpen).toBe(false);
  });

  it('should set and clear session', () => {
    const mockUser = { id: '1', name: 'Test User', email: 'test@example.com' };
    useGlobalStore.getState().setSession(mockUser);
    
    expect(useGlobalStore.getState().user.name).toBe('Test User');
    
    useGlobalStore.getState().clearSession();
    expect(useGlobalStore.getState().user.id).toBe(null);
  });
});
