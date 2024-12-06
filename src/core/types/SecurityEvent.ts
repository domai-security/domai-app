export interface SecurityEvent {
  id: string;
  timestamp: Date;
  source: SecurityEventSource;
  type: SecurityEventType;
  severity: SecurityEventSeverity;
  rawData: string;
  metadata: Record<string, any>;
}

export enum SecurityEventSource {
  TCPDUMP = 'tcpdump',
  SYSTEM_LOG = 'system_log',
  NETWORK_MONITOR = 'network_monitor',
  PROCESS_MONITOR = 'process_monitor',
  FILE_SYSTEM = 'file_system'
}

export enum SecurityEventType {
  NETWORK_CONNECTION = 'network_connection',
  FILE_ACCESS = 'file_access',
  PROCESS_LAUNCH = 'process_launch',
  SYSTEM_CHANGE = 'system_change',
  PERMISSION_CHANGE = 'permission_change'
}

export enum SecurityEventSeverity {
  INFO = 'info',
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}
