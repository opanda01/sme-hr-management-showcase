/**
 * Showcase — Expo (React Native) QR attendance screen (sanitized).
 * Employees check in/out via a dynamic QR shown by the employer; supports deep links and raw token payloads.
 * State machine (loading → scanner → result): checks today's shift and existing record first; debounces duplicate scans.
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Linking,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { CameraView, useCameraPermissions } from 'expo-camera';
import Ionicons from '@expo/vector-icons/Ionicons';

// Production: @/features/attendance/services/attendance.service, auth store, theme hooks
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL; // e.g. https://api.example-acme.test

type ScreenMode = 'loading' | 'scanner' | 'result';

type AttendanceRecord = {
  check_in: string;
  check_out?: string | null;
};

type AuthUser = {
  company_id: string;
  display_name: string; // e.g. "Ayşe Demir — Acme Corp"
};

/** Extract session token from deep link (`acmehr://scan?token=...`) or raw QR payload. */
export function extractQrToken(payload: string): string | null {
  if (!payload) return null;
  try {
    const parsed = new URL(payload);
    const tokenParam = parsed.searchParams.get('token') || parsed.searchParams.get('qr_token');
    if (tokenParam) return tokenParam;
  } catch {
    // Not a URL — treat payload as a raw token string
  }
  return payload;
}

async function checkIn(companyId: string, qrToken: string): Promise<AttendanceRecord> {
  const res = await fetch(`${API_BASE_URL}/companies/${companyId}/attendance/check-in`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer <access_token>' },
    body: JSON.stringify({ qr_token: qrToken }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? 'Yoklama kaydı oluşturulamadı.');
  }
  return res.json();
}

async function checkOut(companyId: string): Promise<AttendanceRecord> {
  const res = await fetch(`${API_BASE_URL}/companies/${companyId}/attendance/check-out`, {
    method: 'POST',
    headers: { Authorization: 'Bearer <access_token>' },
  });
  if (!res.ok) throw new Error('Çıkış yapılamadı.');
  return res.json();
}

export type QRScannerProps = {
  user: AuthUser | null;
  deepLinkToken?: string | null;
  deepLinkCompanyId?: string | null;
};

export function QRScanner({ user, deepLinkToken, deepLinkCompanyId }: QRScannerProps) {
  const [permission, requestPermission] = useCameraPermissions();
  const [mode, setMode] = useState<ScreenMode>('loading');
  const [record, setRecord] = useState<AttendanceRecord | null>(null);
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasShiftToday, setHasShiftToday] = useState<boolean | null>(null);
  const autoCheckInStartedRef = useRef(false);

  const bootstrap = useCallback(async () => {
    if (!user?.company_id) return;
    // Production: getMySchedule + getTodayRecord
    setHasShiftToday(true);
    setMode('scanner');
  }, [user?.company_id]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const submitCheckIn = useCallback(
    async (tokenValue: string) => {
      if (!user?.company_id) return;
      if (hasShiftToday === false) {
        Alert.alert('Uyarı', 'Bugün planlı vardiyanız yok; giriş yapılamaz.', [
          { text: 'Tamam', onPress: () => setScanned(false) },
        ]);
        return;
      }

      setScanned(true);
      setLoading(true);
      try {
        const data = await checkIn(user.company_id, tokenValue);
        setRecord(data);
        setMode('result');
      } catch (e: unknown) {
        const message = e instanceof Error ? e.message : 'Tarama başarısız.';
        Alert.alert('Hata', message, [{ text: 'Tekrar Dene', onPress: () => setScanned(false) }]);
      } finally {
        setLoading(false);
      }
    },
    [user?.company_id, hasShiftToday],
  );

  useEffect(() => {
    if (autoCheckInStartedRef.current || !deepLinkToken || !user?.company_id) return;
    if (mode !== 'scanner' || record || loading) return;

    if (deepLinkCompanyId && deepLinkCompanyId !== user.company_id) {
      autoCheckInStartedRef.current = true;
      Alert.alert('Hata', 'Bu QR kod farklı bir şirkete (tenant) ait.');
      return;
    }

    autoCheckInStartedRef.current = true;
    submitCheckIn(deepLinkToken);
  }, [deepLinkToken, deepLinkCompanyId, user?.company_id, mode, record, loading, submitCheckIn]);

  const handleBarCodeScanned = async ({ data }: { data: string }) => {
    if (scanned || loading) return;
    const tokenValue = extractQrToken(data);
    if (!tokenValue) {
      Alert.alert('Hata', 'QR içeriği geçersiz.');
      return;
    }
    await submitCheckIn(tokenValue);
  };

  if (!permission?.granted) {
    return (
      <SafeAreaView style={styles.centered}>
        <Text style={styles.title}>Kamera izni gerekli</Text>
        <TouchableOpacity style={styles.primaryBtn} onPress={() => requestPermission()}>
          <Text style={styles.primaryBtnText}>İzin ver</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => Linking.openSettings()}>
          <Text style={styles.link}>Ayarlara git</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  if (mode === 'loading') {
    return (
      <SafeAreaView style={styles.centered}>
        <ActivityIndicator size="large" />
        <Text>Yoklama durumu kontrol ediliyor…</Text>
      </SafeAreaView>
    );
  }

  if (mode === 'result' && record) {
    return (
      <SafeAreaView style={styles.centered}>
        <Ionicons name="checkmark-circle-outline" size={72} color="#16a34a" />
        <Text style={styles.title}>Giriş kaydedildi</Text>
        <Text>Giriş: {new Date(record.check_in).toLocaleTimeString('tr-TR')}</Text>
        {!record.check_out ? (
          <TouchableOpacity
            style={[styles.primaryBtn, styles.dangerBtn]}
            onPress={async () => {
              if (!user?.company_id) return;
              const updated = await checkOut(user.company_id);
              setRecord(updated);
            }}
          >
            <Text style={styles.primaryBtnText}>Çıkış yap</Text>
          </TouchableOpacity>
        ) : null}
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.scannerRoot}>
      <CameraView
        style={StyleSheet.absoluteFillObject}
        barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
        onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
      />
      <View style={styles.overlay}>
        <Text style={styles.overlayTitle}>QR yoklama — Acme Corp</Text>
        <Text style={styles.overlayHint}>Kodu çerçeve içine hizalayın</Text>
      </View>
      {loading ? (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator color="#fff" size="large" />
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  centered: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24, gap: 12 },
  scannerRoot: { flex: 1, backgroundColor: '#000' },
  overlay: {
    position: 'absolute',
    top: 48,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  overlayTitle: { color: '#fff', fontSize: 20, fontWeight: '600' },
  overlayHint: { color: 'rgba(255,255,255,0.8)', marginTop: 4 },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.6)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: { fontSize: 18, fontWeight: '600' },
  primaryBtn: {
    backgroundColor: '#0f172a',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 8,
  },
  dangerBtn: { backgroundColor: '#dc2626' },
  primaryBtnText: { color: '#fff', fontWeight: '600' },
  link: { color: '#2563eb', marginTop: 8 },
});

export default QRScanner;
