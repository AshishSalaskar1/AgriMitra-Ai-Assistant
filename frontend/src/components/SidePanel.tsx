import React, { useState } from 'react';
import { X, TrendingUp, FileText, Sprout } from 'lucide-react';
import { marketApi, schemesApi } from '../services/api';

interface SidePanelProps {
  onClose: () => void;
  language: string;
}

export const SidePanel: React.FC<SidePanelProps> = ({ onClose, language }) => {
  const [activeTab, setActiveTab] = useState<'market' | 'schemes' | 'tips'>('market');
  const [marketData, setMarketData] = useState<{ popular_crops: Array<{ name: string; price: number; unit: string; trend: string }> } | null>(null);
  const [schemes, setSchemes] = useState<{ popular_schemes: Array<{ name: string; description: string; category: string }> } | null>(null);
  const [loading, setLoading] = useState(false);

  const loadMarketData = async () => {
    try {
      setLoading(true);
      const popularCrops = await marketApi.getPopularCrops();
      setMarketData(popularCrops);
    } catch (error) {
      console.error('Error loading market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSchemes = async () => {
    try {
      setLoading(true);
      const popularSchemes = await schemesApi.getPopularSchemes();
      setSchemes(popularSchemes);
    } catch (error) {
      console.error('Error loading schemes:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (activeTab === 'market' && !marketData) {
      loadMarketData();
    } else if (activeTab === 'schemes' && !schemes) {
      loadSchemes();
    }
  }, [activeTab, marketData, schemes]);

  const tabs = [
    { 
      id: 'market' as const, 
      label: language === 'kn' ? 'ಮಾರುಕಟ್ಟೆ' : 'Market', 
      icon: TrendingUp 
    },
    { 
      id: 'schemes' as const, 
      label: language === 'kn' ? 'ಯೋಜನೆಗಳು' : 'Schemes', 
      icon: FileText 
    },
    { 
      id: 'tips' as const, 
      label: language === 'kn' ? 'ಸಲಹೆಗಳು' : 'Tips', 
      icon: Sprout 
    }
  ];

  const farmingTips = [
    {
      title: language === 'kn' ? 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ' : 'Soil Testing',
      content: language === 'kn' 
        ? 'ಪ್ರತಿ ವರ್ಷ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಮಾಡಿಸಿ ಮತ್ತು ಸೂಕ್ತ ಗೊಬ್ಬರ ಬಳಸಿ'
        : 'Test your soil annually and use appropriate fertilizers based on results'
    },
    {
      title: language === 'kn' ? 'ನೀರಿನ ನಿರ್ವಹಣೆ' : 'Water Management',
      content: language === 'kn'
        ? 'ಟಪಕ ನೀರಾವರಿ ವ್ಯವಸ್ಥೆ ಬಳಸಿ ನೀರು ಉಳಿಸಿ'
        : 'Use drip irrigation systems to conserve water and improve efficiency'
    },
    {
      title: language === 'kn' ? 'ಬೆಳೆ ಸಂಯೋಜನೆ' : 'Crop Rotation',
      content: language === 'kn'
        ? 'ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಕಾಪಾಡಲು ಬೆಳೆ ಸಂಯೋಜನೆ ಮಾಡಿ'
        : 'Practice crop rotation to maintain soil fertility and reduce pest problems'
    }
  ];

  return (
    <div className="w-80 bg-white border-l border-agri-green-200 shadow-lg animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-agri-green-200">
        <h2 className="text-lg font-semibold text-agri-green-800">
          {language === 'kn' ? 'ಕ್ಷಿಕ ಮಾಹಿತಿ' : 'Farm Information'}
        </h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-agri-green-100 rounded"
        >
          <X className="w-5 h-5 text-agri-green-600" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-agri-green-200">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center space-x-1 py-3 text-sm transition-colors ${
                activeTab === tab.id
                  ? 'bg-agri-green-100 text-agri-green-700 border-b-2 border-agri-green-600'
                  : 'text-agri-green-600 hover:bg-agri-green-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'market' && (
          <div className="space-y-4">
            <h3 className="font-semibold text-agri-green-800">
              {language === 'kn' ? 'ಇಂದಿನ ದರಗಳು' : "Today's Prices"}
            </h3>
            {loading ? (
              <div className="text-center py-4 text-agri-green-600">
                {language === 'kn' ? 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...' : 'Loading...'}
              </div>
            ) : marketData?.popular_crops ? (
              <div className="space-y-3">
                {marketData.popular_crops.map((crop, index: number) => (
                  <div key={index} className="bg-agri-green-50 rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-agri-green-800">{crop.name}</span>
                      <span className="text-agri-green-600">₹{crop.price} {crop.unit}</span>
                    </div>
                    <div className={`text-xs mt-1 ${
                      crop.trend === 'increasing' ? 'text-green-600' : 
                      crop.trend === 'decreasing' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {crop.trend === 'increasing' ? '↗️' : crop.trend === 'decreasing' ? '↘️' : '→'} 
                      {crop.trend}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-agri-green-600">
                {language === 'kn' ? 'ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ' : 'No market data available'}
              </div>
            )}
          </div>
        )}

        {activeTab === 'schemes' && (
          <div className="space-y-4">
            <h3 className="font-semibold text-agri-green-800">
              {language === 'kn' ? 'ಜನಪ್ರಿಯ ಯೋಜನೆಗಳು' : 'Popular Schemes'}
            </h3>
            {loading ? (
              <div className="text-center py-4 text-agri-green-600">
                {language === 'kn' ? 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...' : 'Loading...'}
              </div>
            ) : schemes?.popular_schemes ? (
              <div className="space-y-3">
                {schemes.popular_schemes.map((scheme, index: number) => (
                  <div key={index} className="bg-agri-green-50 rounded-lg p-3">
                    <h4 className="font-medium text-agri-green-800 text-sm">{scheme.name}</h4>
                    <p className="text-xs text-agri-green-600 mt-1 line-clamp-2">
                      {scheme.description}
                    </p>
                    <div className="mt-2">
                      <span className="inline-block bg-agri-green-200 text-agri-green-700 text-xs px-2 py-1 rounded">
                        {scheme.category}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-agri-green-600">
                {language === 'kn' ? 'ಯೋಜನೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ' : 'No schemes data available'}
              </div>
            )}
          </div>
        )}

        {activeTab === 'tips' && (
          <div className="space-y-4">
            <h3 className="font-semibold text-agri-green-800">
              {language === 'kn' ? 'ಕೃಷಿ ಸಲಹೆಗಳು' : 'Farming Tips'}
            </h3>
            <div className="space-y-3">
              {farmingTips.map((tip, index) => (
                <div key={index} className="bg-agri-green-50 rounded-lg p-3">
                  <h4 className="font-medium text-agri-green-800 text-sm">{tip.title}</h4>
                  <p className="text-xs text-agri-green-600 mt-1">{tip.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
