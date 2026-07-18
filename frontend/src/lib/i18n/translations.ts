export type Locale = "en" | "hi" | "gu";

export const localeLabels: Record<Locale, string> = {
  en: "English",
  hi: "हिन्दी",
  gu: "ગુજરાતી",
};

type TranslationKeys =
  | "appName"
  | "tagline"
  | "navHome"
  | "navElder"
  | "navFamily"
  | "navCalendar"
  | "navLogin"
  | "navRegister"
  | "navLogout"
  | "landingTitle"
  | "landingSubtitle"
  | "landingElderCta"
  | "landingFamilyCta"
  | "landingDemoCta"
  | "loginTitle"
  | "registerTitle"
  | "email"
  | "password"
  | "fullName"
  | "role"
  | "roleFamily"
  | "roleElder"
  | "familyName"
  | "inviteCode"
  | "submit"
  | "noAccount"
  | "hasAccount"
  | "elderWelcome"
  | "familyWelcome"
  | "yourRoutines"
  | "routinesHint"
  | "tryReminder"
  | "sendingReminder"
  | "voiceReplies"
  | "send"
  | "chatPlaceholder"
  | "chatEmptyTitle"
  | "chatEmptyText"
  | "thinking"
  | "sources"
  | "sos"
  | "sosConfirm"
  | "sosSent"
  | "wellnessTitle"
  | "wellnessSubmit"
  | "mood"
  | "appetite"
  | "sleep"
  | "calendarTitle"
  | "calendarEmpty"
  | "familySummaryTitle"
  | "medicinesToday"
  | "ateToday"
  | "feelingToday"
  | "unusualToday"
  | "needsAttention"
  | "healthScore"
  | "activityTimeline"
  | "addElder"
  | "elderName"
  | "sessionId"
  | "inviteShare"
  | "noElders"
  | "notifications"
  | "yes"
  | "no"
  | "unknown"
  | "backendConnected"
  | "backendOffline";

export type Translations = Record<TranslationKeys, string>;

export const translations: Record<Locale, Translations> = {
  en: {
    appName: "Sahaay",
    tagline: "Your gentle care companion",
    navHome: "Home",
    navElder: "Companion",
    navFamily: "Family hub",
    navCalendar: "Schedule",
    navLogin: "Log in",
    navRegister: "Sign up",
    navLogout: "Log out",
    landingTitle: "Care for loved ones, even from far away",
    landingSubtitle:
      "Sahaay listens, remembers routines, answers health questions, and keeps families gently informed.",
    landingElderCta: "Open elder companion",
    landingFamilyCta: "Open family dashboard",
    landingDemoCta: "Try quick demo",
    loginTitle: "Welcome back",
    registerTitle: "Create your account",
    email: "Email",
    password: "Password",
    fullName: "Full name",
    role: "I am a",
    roleFamily: "Family member",
    roleElder: "Elder",
    familyName: "Family name",
    inviteCode: "Invite code (optional)",
    submit: "Continue",
    noAccount: "Need an account?",
    hasAccount: "Already have an account?",
    elderWelcome: "Namaste — Sahaay is here with you",
    familyWelcome: "Family dashboard",
    yourRoutines: "Your routines",
    routinesHint:
      "Sahaay remembers what you share — medicines, bills, and daily habits.",
    tryReminder: "Try demo reminder",
    sendingReminder: "Sending reminder…",
    voiceReplies: "Voice replies",
    send: "Send",
    chatPlaceholder: "Type a message…",
    chatEmptyTitle: "Namaste — welcome to Sahaay",
    chatEmptyText:
      "Share your daily routines or ask a health question. Sahaay listens gently and remembers what matters to you.",
    thinking: "Sahaay is thinking…",
    sources: "Sources",
    sos: "SOS — alert family",
    sosConfirm: "Send an urgent alert to your family?",
    sosSent: "Family has been notified. Help is on the way.",
    wellnessTitle: "How are you feeling today?",
    wellnessSubmit: "Save wellness check",
    mood: "Mood",
    appetite: "Appetite",
    sleep: "Sleep",
    calendarTitle: "Your calendar",
    calendarEmpty: "No scheduled routines yet. Share them in chat first.",
    familySummaryTitle: "Today's care summary",
    medicinesToday: "Medicines taken today?",
    ateToday: "Ate properly today?",
    feelingToday: "How are they feeling?",
    unusualToday: "Anything unusual?",
    needsAttention: "Needs your attention?",
    healthScore: "Wellness score",
    activityTimeline: "Activity timeline",
    addElder: "Add elder profile",
    elderName: "Elder's name",
    sessionId: "Chat session ID",
    inviteShare: "Share this invite code with family",
    noElders: "Add an elder profile to start tracking care.",
    notifications: "Notifications",
    yes: "Yes",
    no: "No",
    unknown: "Not recorded yet",
    backendConnected: "Backend connected",
    backendOffline: "Backend offline",
  },
  hi: {
    appName: "सहाय",
    tagline: "आपका कोमल देखभाल साथी",
    navHome: "होम",
    navElder: "साथी",
    navFamily: "परिवार केंद्र",
    navCalendar: "दिनचर्या",
    navLogin: "लॉग इन",
    navRegister: "साइन अप",
    navLogout: "लॉग आउट",
    landingTitle: "दूर रहकर भी प्रियजनों की देखभाल",
    landingSubtitle:
      "सहाय सुनता है, दिनचर्या याद रखता है, स्वास्थ्य सवालों के जवाब देता है, और परिवार को सूचित रखता है।",
    landingElderCta: "बुजुर्ग साथी खोलें",
    landingFamilyCta: "परिवार डैशबोर्ड",
    landingDemoCta: "त्वरित डेमो",
    loginTitle: "वापस स्वागत है",
    registerTitle: "खाता बनाएं",
    email: "ईमेल",
    password: "पासवर्ड",
    fullName: "पूरा नाम",
    role: "मैं हूँ",
    roleFamily: "परिवार सदस्य",
    roleElder: "बुजुर्ग",
    familyName: "परिवार का नाम",
    inviteCode: "आमंत्रण कोड (वैकल्पिक)",
    submit: "आगे बढ़ें",
    noAccount: "खाता नहीं है?",
    hasAccount: "पहले से खाता है?",
    elderWelcome: "नमस्ते — सहाय आपके साथ है",
    familyWelcome: "परिवार डैशबोर्ड",
    yourRoutines: "आपकी दिनचर्या",
    routinesHint:
      "सहाय आपकी दवाइयाँ, बिल और दैनिक आदतें याद रखता है।",
    tryReminder: "डेमो अनुस्मारक",
    sendingReminder: "भेजा जा रहा है…",
    voiceReplies: "आवाज़ में जवाब",
    send: "भेजें",
    chatPlaceholder: "संदेश लिखें…",
    chatEmptyTitle: "नमस्ते — सहाय में स्वागत है",
    chatEmptyText:
      "अपनी दिनचर्या साझा करें या स्वास्थ्य सवाल पूछें। सहाय धीरे से सुनता है।",
    thinking: "सहाय सोच रहा है…",
    sources: "स्रोत",
    sos: "SOS — परिवार को सूचित करें",
    sosConfirm: "परिवार को तुरंत सूचना भेजें?",
    sosSent: "परिवार को सूचित कर दिया गया है।",
    wellnessTitle: "आज आप कैसा महसूस कर रहे हैं?",
    wellnessSubmit: "वेलनेस सेव करें",
    mood: "मूड",
    appetite: "भूख",
    sleep: "नींद",
    calendarTitle: "आपका कैलेंडर",
    calendarEmpty: "अभी कोई दिनचर्या नहीं। पहले चैट में बताएं।",
    familySummaryTitle: "आज की देखभाल सारांश",
    medicinesToday: "आज दवाइयाँ ली?",
    ateToday: "आज ठीक से खाया?",
    feelingToday: "वे कैसा महसूस कर रहे हैं?",
    unusualToday: "कुछ असामान्य?",
    needsAttention: "ध्यान चाहिए?",
    healthScore: "वेलनेस स्कोर",
    activityTimeline: "गतिविधि",
    addElder: "बुजुर्ग प्रोफ़ाइल जोड़ें",
    elderName: "बुजुर्ग का नाम",
    sessionId: "चैट सत्र ID",
    inviteShare: "परिवार के साथ आमंत्रण कोड साझा करें",
    noElders: "देखभाल शुरू करने के लिए बुजुर्ग जोड़ें।",
    notifications: "सूचनाएँ",
    yes: "हाँ",
    no: "नहीं",
    unknown: "अभी दर्ज नहीं",
    backendConnected: "बैकएंड जुड़ा है",
    backendOffline: "बैकएंड ऑफ़लाइन",
  },
  gu: {
    appName: "સહાય",
    tagline: "તમારો સૌમ્ય સંભાળ સાથી",
    navHome: "હોમ",
    navElder: "સાથી",
    navFamily: "પરિવાર કેન્દ્ર",
    navCalendar: "દિનચર્યા",
    navLogin: "લોગ ઇન",
    navRegister: "સાઇન અપ",
    navLogout: "લોગ આઉટ",
    landingTitle: "દૂરથી પણ પ્રિયજનોની સંભાળ",
    landingSubtitle:
      "સહાય સાંભળે છે, દિનચર્યા યાદ રાખે છે, આરોગ્ય પ્રશ્નોના જવાબ આપે છે, અને પરિવારને જાણ કરે છે.",
    landingElderCta: "વૃદ્ધ સાથી ખોલો",
    landingFamilyCta: "પરિવાર ડેશબોર્ડ",
    landingDemoCta: "ઝડપી ડેમો",
    loginTitle: "પાછા સ્વાગત",
    registerTitle: "ખાતું બનાવો",
    email: "ઈમેલ",
    password: "પાસવર્ડ",
    fullName: "પૂરું નામ",
    role: "હું છું",
    roleFamily: "પરિવાર સભ્ય",
    roleElder: "વૃદ્ધ",
    familyName: "પરિવારનું નામ",
    inviteCode: "આમંત્રણ કોડ (વૈકલ્પિક)",
    submit: "આગળ વધો",
    noAccount: "ખાતું નથી?",
    hasAccount: "પહેલેથી ખાતું છે?",
    elderWelcome: "નમસ્તે — સહાય તમારી સાથે છે",
    familyWelcome: "પરિવાર ડેશબોર્ડ",
    yourRoutines: "તમારી દિનચર્યા",
    routinesHint:
      "સહાય દવાઓ, બિલ અને દૈનિક ટેવ યાદ રાખે છે.",
    tryReminder: "ડેમો રીમાઇન્ડર",
    sendingReminder: "મોકલી રહ્યા છીએ…",
    voiceReplies: "અવાજમાં જવાબ",
    send: "મોકલો",
    chatPlaceholder: "સંદેશ લખો…",
    chatEmptyTitle: "નમસ્તે — સહાયમાં સ્વાગત",
    chatEmptyText:
      "તમારી દિનચર્યા શેર કરો અથવા આરોગ્ય પ્રશ્ન પૂછો. સહાય ધીરે સાંભળે છે.",
    thinking: "સહાય વિચારી રહ્યો છે…",
    sources: "સ્રોત",
    sos: "SOS — પરિવારને જાણ",
    sosConfirm: "પરિવારને તાત્કાલિક જાણ મોકલવી?",
    sosSent: "પરિવારને જાણ કરી દીધી છે.",
    wellnessTitle: "આજે તમે કેવું અનુભવો છો?",
    wellnessSubmit: "વેલનેસ સાચવો",
    mood: "મૂડ",
    appetite: "ભૂખ",
    sleep: "નિદ્રા",
    calendarTitle: "તમારું કેલેન્ડર",
    calendarEmpty: "હજુ દિનચર્યા નથી. પહેલા ચેટમાં કહો.",
    familySummaryTitle: "આજની સંભાળ સારાંશ",
    medicinesToday: "આજે દવા લીધી?",
    ateToday: "આજે યોગ્ય ખાધું?",
    feelingToday: "તેઓ કેવું અનુભવે છે?",
    unusualToday: "કંઈ અસામાન્ય?",
    needsAttention: "ધ્યાન જોઈએ?",
    healthScore: "વેલનેસ સ્કોર",
    activityTimeline: "પ્રવૃત્તિ",
    addElder: "વૃદ્ધ પ્રોફાઇલ ઉમેરો",
    elderName: "વૃદ્ધનું નામ",
    sessionId: "ચેટ સત્ર ID",
    inviteShare: "પરિવાર સાથે આમંત્રણ કોડ શેર કરો",
    noElders: "સંભાળ શરૂ કરવા વૃદ્ધ ઉમેરો.",
    notifications: "સૂચનાઓ",
    yes: "હા",
    no: "ના",
    unknown: "હજુ નોંધાયું નથી",
    backendConnected: "બેકએન્ડ જોડાયેલ",
    backendOffline: "બેકએન્ડ ઑફલાઇન",
  },
};

export function t(locale: Locale, key: TranslationKeys): string {
  return translations[locale][key];
}
