export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Добро пожаловать в АГОРА</h1>
          <p className="text-lg text-gray-600 mb-6">
            Платформа для проведения технических интервью с AI-ассистентом.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-blue-800 mb-2">Интервью</h2>
              <p className="text-gray-600">
                Генерируйте вопросы для интервью и записывайте свои ответы.
              </p>
            </div>
            <div className="bg-green-50 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-green-800 mb-2">Настройки</h2>
              <p className="text-gray-600">
                Настройте параметры записи и продолжительность ответов.
              </p>
            </div>
            <div className="bg-purple-50 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-purple-800 mb-2">История</h2>
              <p className="text-gray-600">
                Просмотрите историю ваших интервью и ответов.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
