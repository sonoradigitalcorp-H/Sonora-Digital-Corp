import { NextResponse } from 'next/server';
import { getNotifications, refreshNotifications, markNotificationRead, markAllNotificationsRead } from '@/lib/data-generator';

export async function GET() {
  const notifications = getNotifications();
  const unread = notifications.filter(n => !n.read).length;
  return NextResponse.json({
    notifications,
    unread,
    total: notifications.length,
  });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const { action, id } = body;

  if (action === 'refresh') {
    const notifications = refreshNotifications();
    return NextResponse.json({
      notifications,
      unread: notifications.filter(n => !n.read).length,
      total: notifications.length,
      refreshed: true,
    });
  }

  if (action === 'mark_read' && id) {
    markNotificationRead(id);
  } else if (action === 'mark_all_read') {
    markAllNotificationsRead();
  }

  const notifications = getNotifications();
  const unread = notifications.filter(n => !n.read).length;
  return NextResponse.json({ success: true, unread, notifications });
}
