# aztrotech-booking — AztroTech Custom Booking

**Version**: 1.0.0
**Tenant**: aztrotech

---

## 1. Business Objective

Allow Mystic (AztroTech sales assistant) to manage César's calendar directly —
propose available slots, confirm bookings, and notify César — without any
external platform like Cal.com.

## 2. Inputs

```gherkin
Given a prospect wants to schedule a free diagnostic with César
When Mystic needs to check available times
Or confirm a booking
Or cancel a booking
```

## 3. Outputs

```gherkin
Then available time slots are returned to Mystic
And the booking is saved to AztroTech's calendar store
And César is notified via Telegram with prospect details
```

## 4. Tools

```
Tools:
- aztrotech_calendar_available(slots): list free time slots for a given day
- aztrotech_calendar_book(name, email, phone, company, date, time): confirm booking
- aztrotech_calendar_cancel(booking_id): cancel a booking
```

## 5. Dependencies

```
Dependencies:
- clients/aztrotech/calendar/: booking engine
- Telegram bot token: @Aztro_tech_bot
- OpenClaw gateway: port 18789
```

## 6. Configuration

```yaml
calendar_system: custom
availability:
  monday-friday: "09:00-18:00"
  saturday: "09:00-14:00"
  slot_duration_minutes: 15
timezone: America/Hermosillo
```

## 7. Policies

```
Policies:
- Slots are 15 minutes with no buffer
- Bookings are stored locally in clients/aztrotech/calendar/bookings.json
- César is notified via Telegram on every new booking
- Prospect can cancel within 2 hours of booking
```

## 8. Success Metrics

```gherkin
Success Metrics:
- booking_time: Given prospect agrees When booking confirmed Then seconds
  Target: < 30 s
- notification_delivery: Given booking saved When César notified Then seconds
  Target: < 5 s
```

## 9. Failure Conditions

```
Failure Conditions:
- Bookings file corrupted: reset to empty array
- Telegram unreachable: log notification, retry on next message
- Double booking: check availability before confirming
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If bookings.json corrupted → backup to .corrupted, create fresh
2. If Telegram fails → queue notification, retry every 60s
3. If slot conflict → show updated availability to prospect
```

## 11. Parent OS

```
Parent OS: Sales — AztroTech
```
