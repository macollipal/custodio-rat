'use client';

import { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  options?: { label: string; value: string }[];
}

interface ChatOption {
  label: string;
  value: string;
}

interface ChatResponse {
  response: string;
  options?: ChatOption[];
  timestamp?: string;
  sessionId?: string;
}

const N8N_WEBHOOK_URL = 'https://emece.app.n8n.cloud/webhook/chatbot-custodio';

const INITIAL_MESSAGE: ChatMessage = {
  role: 'assistant',
  content: '👋 Hola, soy el asistente de Protección de Datos.\n\n¿En qué puedo ayudarte hoy?\n\n1️⃣ Conocer mis derechos\n2️⃣ Qué es un RAT y cómo crear uno\n3️⃣ Reportar una brecha de seguridad\n4️⃣ Ver todas las opciones',
  options: [
    { label: 'Conocer mis derechos', value: 'opcion1' },
    { label: 'Qué es un RAT y crear uno', value: 'opcion2' },
    { label: 'Reportar una brecha', value: 'opcion3' },
    { label: 'Ver todas las opciones', value: 'opcion4' },
  ],
};

const TYPING_DELAY = 30;

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `custodio-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, messages]);

  const sendToN8N = async (message: string): Promise<ChatResponse | null> => {
    try {
      const response = await fetch(N8N_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          sessionId,
          userId: sessionStorage.getItem('custodio_user') || 'anonymous',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error communicating with n8n:', error);
      return null;
    }
  };

  const handleOptionClick = async (option: ChatOption) => {
    const userMessage: ChatMessage = { role: 'user', content: option.label };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    await new Promise(resolve => setTimeout(resolve, TYPING_DELAY));

    let responseText = '';
    let newOptions: ChatOption[] | undefined;

    switch (option.value) {
      case 'opcion1':
        responseText = `📋 **Derechos ARCO**\n\nLa Ley 21.719 garantiza tus derechos:\n\n• **Acceso**: Conocer qué datos tuyos se están tratando\n• **Rectificación**: Corregir datos inexactos o incompletos\n• **Cancelación**: Eliminar tus datos (con excepciones)\n• **Oposición**: Oponerte al tratamiento de tus datos\n\n¿Deseas más información sobre algún derecho específico?`;
        newOptions = [
          { label: 'Volver al menú', value: 'menu' },
          { label: 'Más sobre derechos ARCO', value: 'opcion1_detail' },
        ];
        break;
      case 'opcion2':
        responseText = `📝 **Guía RAT - Registro de Actividades de Tratamiento**\n\nUn RAT es un registro obligatorio que documenta todas las actividades de tratamiento de datos personales de una organización.\n\n**¿Qué información debe incluir?**\n• Nombre del proceso\n• Categoría de datos tratados\n• Finalidad del tratamiento\n• Base legal (consentimiento, contrato, obligación legal, etc.)\n• Plazo de retención\n\n**¿Cómo crear uno en CUSTODIO?**\n1. Ve a la sección "Procesos RAT"\n2. Click en "Nuevo RAT"\n3. Completa el asistente paso a paso\n4. Guarda y verifica la completitud\n\n¿Deseas que te guíe en algún paso específico?`;
        newOptions = [
          { label: 'Volver al menú', value: 'menu' },
          { label: 'Crear un RAT ahora', value: 'crear_rat' },
          { label: 'Saber más sobre bases legales', value: 'bases_legales' },
        ];
        break;
      case 'opcion3':
        responseText = `🚨 **Reporte de Brechas de Seguridad**\n\nSi detectaste una brecha de seguridad (acceso no autorizado, pérdida de datos, etc.):\n\n**Pasos a seguir:**\n1. Documenta qué ocurrió y cuándo\n2. Evalúa el alcance (cuántos afectados, qué datos)\n3. Notifica a la APDP (Autoridad de Protección de Datos) en máximo 72 horas\n4. Si hay datos sensibles comprometidos, notifica a los afectados\n\n**En CUSTODIO:**\nVe a la sección "Brechas" para registrar y gestionar incidentes.\n\n¿Necesitas ayuda con algún paso específico?`;
        newOptions = [
          { label: 'Volver al menú', value: 'menu' },
          { label: 'Registrar una brecha', value: 'registrar_brecha' },
        ];
        break;
      case 'opcion4':
        responseText = `📚 **Temas disponibles**\n\n1️⃣ **Derechos ARCO** - Conoce tus derechos como titular de datos\n2️⃣ **RAT** - Qué es y cómo crear un Registro de Actividades de Tratamiento\n3️⃣ **Brechas de seguridad** - Cómo reportar y gestionar incidentes\n4️⃣ **Sanciones** - Consecuencias del incumplimiento\n5️⃣ **Datos sensibles** - Categorías especiales de datos\n6️⃣ **Transferencias internacionales** - Envío de datos fuera de Chile\n\nSelecciona un tema para más información.`;
        newOptions = [
          { label: 'Derechos ARCO', value: 'opcion1' },
          { label: 'RAT', value: 'opcion2' },
          { label: 'Brechas', value: 'opcion3' },
          { label: 'Sanciones', value: 'opcion5' },
          { label: 'Volver al menú', value: 'menu' },
        ];
        break;
      case 'menu':
        setMessages([INITIAL_MESSAGE]);
        setIsLoading(false);
        return;
      default:
        const n8nResponse = await sendToN8N(option.label);
        if (n8nResponse) {
          responseText = n8nResponse.response;
          newOptions = n8nResponse.options;
        } else {
          responseText = 'Lo siento, no pude procesar tu solicitud. ¿Deseas volver al menú principal?';
          newOptions = [{ label: 'Volver al menú', value: 'menu' }];
        }
    }

    setMessages(prev => [
      ...prev,
      {
        role: 'assistant',
        content: responseText,
        options: newOptions,
      },
    ]);
    setIsLoading(false);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const n8nResponse = await sendToN8N(input.trim());

    await new Promise(resolve => setTimeout(resolve, TYPING_DELAY));

    if (n8nResponse) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: n8nResponse.response,
          options: n8nResponse.options,
        },
      ]);
    } else {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Lo siento, estoy teniendo dificultades para conectarme. Por favor intenta más tarde o contacta a soporte.',
          options: [{ label: 'Volver al menú', value: 'menu' }],
        },
      ]);
      toast.error('Error de conexión con el asistente');
    }
    setIsLoading(false);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center text-2xl transition hover:scale-105 z-40"
        style={{ background: 'linear-gradient(135deg, #2563EB, #7C3AED)', color: 'white' }}
        title="Asistente de Protección de Datos"
      >
        🤖
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end" onClick={() => setIsOpen(false)}>
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
          <div
            className="relative flex flex-col h-full shadow-2xl overflow-hidden"
            style={{ width: '95vw', maxWidth: 420, background: 'white', animation: 'slideInRight 0.25s ease' }}
            onClick={e => e.stopPropagation()}
          >
            <div
              className="flex items-center justify-between px-5 py-4 flex-shrink-0"
              style={{ borderBottom: '1px solid #E5E7EB', background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}
            >
              <div className="flex items-center gap-2">
                <span className="text-xl">🤖</span>
                <div>
                  <h2 className="text-sm font-semibold text-white">Asistente de Protección de Datos</h2>
                  <p className="text-xs text-white/70">Ley 21.719 Chile</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center transition hover:bg-white/20 text-white"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ background: '#F9FAFB' }}>
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className="max-w-[85%] px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap"
                    style={{
                      background: msg.role === 'user' ? 'linear-gradient(135deg, #2563EB, #7C3AED)' : 'white',
                      color: msg.role === 'user' ? 'white' : '#111827',
                      border: msg.role === 'assistant' ? '1px solid #E5E7EB' : 'none',
                      borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                      borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px',
                    }}
                  >
                    {msg.content}
                    {msg.options && msg.options.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {msg.options.map((opt, idx) => (
                          <button
                            key={idx}
                            onClick={() => !isLoading && handleOptionClick(opt)}
                            className="px-3 py-1.5 rounded-full text-xs font-medium transition hover:opacity-90"
                            style={{
                              background: msg.role === 'user' ? 'rgba(255,255,255,0.2)' : '#EFF6FF',
                              color: msg.role === 'user' ? 'white' : '#2563EB',
                              border: msg.role === 'user' ? '1px solid rgba(255,255,255,0.3)' : '1px solid #BFDBFE',
                            }}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="px-4 py-3 rounded-2xl text-sm" style={{ background: 'white', border: '1px solid #E5E7EB', color: '#9CA3AF' }}>
                    Escribiendo...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 flex gap-2 flex-shrink-0" style={{ borderTop: '1px solid #E5E7EB', background: 'white' }}>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
                placeholder="Escribe tu pregunta..."
                className="flex-1 px-3 py-2 rounded-xl text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ borderColor: '#E5E7EB' }}
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="px-4 py-2 rounded-xl text-sm font-semibold text-white transition disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #2563EB, #7C3AED)' }}
              >
                →
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}