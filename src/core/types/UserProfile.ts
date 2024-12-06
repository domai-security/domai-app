export interface UserProfile {
  id: string;
  expertiseLevel: ExpertiseLevel;
  preferences: UserPreferences;
  learningProgress: LearningProgress;
}

export enum ExpertiseLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert'
}

export interface UserPreferences {
  technicalDepth: number;
  automationLevel: number;
  notificationSettings: NotificationSettings;
  privacySettings: PrivacySettings;
}

export interface LearningProgress {
  completedTopics: string[];
  skillLevels: Record<string, number>;
  achievements: Achievement[];
  lastAssessment: Date;
}

export interface NotificationSettings {
  enabled: boolean;
  minSeverity: SecurityEventSeverity;
  channels: NotificationChannel[];
}

export interface PrivacySettings {
  dataCollection: boolean;
  analysisStorage: boolean;
  cloudSync: boolean;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  dateEarned: Date;
}

export enum NotificationChannel {
  IN_APP = 'in_app',
  SYSTEM = 'system',
  EMAIL = 'email'
}
