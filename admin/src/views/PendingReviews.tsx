import React, { useState, useEffect } from 'react';
import { FileText, CheckCircle, XCircle, Eye, Loader2, Upload, Calendar, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';
import { BentoBox } from '../components/ui/BentoBox';

export const PendingReviews: React.FC = () => {
    const [reviews, setReviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [selectedReview, setSelectedReview] = useState<any>(null);
    const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
    const [editedData, setEditedData] = useState<any>({});
    const [reviewNotes, setReviewNotes] = useState('');
    const [actionLoading, setActionLoading] = useState(false);

    // Upload modal state
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
    const [uploadFile, setUploadFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        fetchReviews();
    }, []);

    const fetchReviews = async () => {
        try {
            setLoading(true);
            const data = await api.getPendingReviews();
            setReviews(data || []);
            setError('');
        } catch (err: any) {
            console.error('Failed to fetch reviews:', err);
            setError(err.response?.data?.detail || err.message || 'Failed to load reviews');
        } finally {
            setLoading(false);
        }
    };

    const handleReviewClick = (review: any) => {
        setSelectedReview(review);
        setEditedData(review.parsed_data || {});
        setReviewNotes('');
        setIsReviewModalOpen(true);
    };

    const handleApprove = async () => {
        if (!selectedReview) return;

        try {
            setActionLoading(true);
            await api.approvePendingReview(selectedReview.id, editedData, reviewNotes);

            // Refresh list
            await fetchReviews();

            setIsReviewModalOpen(false);
            setSelectedReview(null);
        } catch (err: any) {
            console.error('Failed to approve:', err);
            alert('Failed to approve review: ' + (err.response?.data?.detail || err.message));
        } finally {
            setActionLoading(false);
        }
    };

    const handleReject = async () => {
        if (!selectedReview) return;

        const reason = prompt('请输入拒绝原因：');
        if (!reason) return;

        try {
            setActionLoading(true);
            await api.rejectPendingReview(selectedReview.id, reason);

            // Refresh list
            await fetchReviews();

            setIsReviewModalOpen(false);
            setSelectedReview(null);
        } catch (err: any) {
            console.error('Failed to reject:', err);
            alert('Failed to reject review: ' + (err.response?.data?.detail || err.message));
        } finally {
            setActionLoading(false);
        }
    };

    const handleUpload = async () => {
        if (!uploadFile) {
            alert('请选择文件');
            return;
        }

        try {
            setUploading(true);
            const result = await api.uploadInsuranceDocument(uploadFile);

            alert(`文档上传成功！\nAI 置信度: ${(result.ai_confidence * 100).toFixed(0)}%\n等待审核中...`);

            // Refresh list
            await fetchReviews();

            setIsUploadModalOpen(false);
            setUploadFile(null);
        } catch (err: any) {
            console.error('Failed to upload:', err);
            alert('上传失败: ' + (err.response?.data?.detail || err.message));
        } finally {
            setUploading(false);
        }
    };

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 0.8) return 'text-electric-green';
        if (confidence >= 0.5) return 'text-yellow-400';
        return 'text-signal-orange';
    };

    const getEntityTypeBadge = (type: string) => {
        const badges: Record<string, { label: string; color: string }> = {
            insurance: { label: '保险', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
            transaction: { label: '交易', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
            asset: { label: '资产', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
            liability: { label: '负债', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
            gov_benefit: { label: '政府福利', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' }
        };

        const badge = badges[type] || badges.insurance;

        return (
            <span className={`text-xs px-2 py-1 rounded border ${badge.color}`}>
                {badge.label}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="p-6 h-full flex items-center justify-center">
                <div className="text-center">
                    <Loader2 size={48} className="mx-auto mb-4 text-neon-purple animate-spin" />
                    <h2 className="text-xl font-bold text-white">加载待审核项...</h2>
                    <p className="text-gray-400">从数据库获取数据</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 h-full flex items-center justify-center">
                <div className="text-center">
                    <XCircle size={48} className="mx-auto mb-4 text-signal-orange" />
                    <h2 className="text-xl font-bold text-white">加载失败</h2>
                    <p className="text-gray-400 mb-4">{error}</p>
                    <button
                        onClick={fetchReviews}
                        className="bg-neon-purple hover:bg-purple-600 text-white px-6 py-2 rounded-lg font-medium"
                    >
                        重试
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 h-full overflow-y-auto">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-light text-white mb-1 tracking-tight">
                        文档审核 <span className="text-gray-500">队列</span>
                    </h1>
                    <p className="text-gray-500 text-sm">AI 扫描 • 人工审核 • 自动导入</p>
                </div>
                <button
                    onClick={() => setIsUploadModalOpen(true)}
                    className="bg-electric-green hover:bg-green-500 text-black font-bold px-4 py-2 rounded-lg flex items-center gap-2"
                >
                    <Upload size={18} />
                    上传文档
                </button>
            </header>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <BentoBox className="bg-gradient-to-br from-blue-900/40 to-black border-blue-500/30">
                    <div className="flex items-center gap-3">
                        <FileText size={24} className="text-blue-400" />
                        <div>
                            <div className="text-2xl font-mono text-white">{reviews.length}</div>
                            <div className="text-xs text-gray-400">待审核</div>
                        </div>
                    </div>
                </BentoBox>

                <BentoBox className="bg-gradient-to-br from-green-900/40 to-black border-green-500/30">
                    <div className="flex items-center gap-3">
                        <TrendingUp size={24} className="text-green-400" />
                        <div>
                            <div className="text-2xl font-mono text-white">
                                {reviews.length > 0 ? ((reviews.reduce((sum, r) => sum + (r.ai_confidence || 0), 0) / reviews.length) * 100).toFixed(0) : 0}%
                            </div>
                            <div className="text-xs text-gray-400">平均 AI 置信度</div>
                        </div>
                    </div>
                </BentoBox>

                <BentoBox className="bg-gradient-to-br from-purple-900/40 to-black border-purple-500/30">
                    <div className="flex items-center gap-3">
                        <Calendar size={24} className="text-purple-400" />
                        <div>
                            <div className="text-2xl font-mono text-white">
                                {reviews.filter(r => {
                                    const createdDate = new Date(r.created_at);
                                    const today = new Date();
                                    return createdDate.toDateString() === today.toDateString();
                                }).length}
                            </div>
                            <div className="text-xs text-gray-400">今日新增</div>
                        </div>
                    </div>
                </BentoBox>
            </div>

            {/* Reviews List */}
            {reviews.length === 0 ? (
                <div className="text-center py-16">
                    <FileText size={64} className="mx-auto mb-4 text-gray-600 opacity-30" />
                    <h3 className="text-xl font-bold text-white mb-2">暂无待审核项</h3>
                    <p className="text-gray-400 mb-6">点击"上传文档"开始扫描保险单、收据等文件</p>
                    <button
                        onClick={() => setIsUploadModalOpen(true)}
                        className="bg-neon-purple hover:bg-purple-600 text-white px-6 py-3 rounded-lg font-medium"
                    >
                        <Upload size={18} className="inline mr-2" />
                        上传第一份文档
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {reviews.map((review) => (
                        <BentoBox key={review.id} className="relative group cursor-pointer hover:border-neon-purple/50 transition-colors">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <FileText size={20} className="text-blue-400" />
                                    <div>
                                        <div className="text-white font-medium">
                                            {review.parsed_data?.provider || review.parsed_data?.name || '未命名文档'}
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            {review.document?.file_name || 'N/A'}
                                        </div>
                                    </div>
                                </div>
                                {getEntityTypeBadge(review.entity_type)}
                            </div>

                            <div className="space-y-2 text-sm mb-4">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">AI 置信度</span>
                                    <span className={`font-mono font-bold ${getConfidenceColor(review.ai_confidence || 0)}`}>
                                        {((review.ai_confidence || 0) * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">上传时间</span>
                                    <span className="text-gray-300">
                                        {new Date(review.created_at).toLocaleDateString('zh-CN')}
                                    </span>
                                </div>
                                {review.parsed_data?.premium && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">保费</span>
                                        <span className="text-white font-mono">
                                            ${review.parsed_data.premium}/{review.parsed_data.frequency === 'Monthly' ? '月' : '年'}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleReviewClick(review)}
                                    className="flex-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-500/30 px-4 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                                >
                                    <Eye size={16} />
                                    审核
                                </button>
                            </div>
                        </BentoBox>
                    ))}
                </div>
            )}

            {/* Review Modal */}
            <AnimatePresence>
                {isReviewModalOpen && selectedReview && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                            onClick={() => setIsReviewModalOpen(false)}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-3xl relative z-10 shadow-2xl max-h-[90vh] overflow-y-auto"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <div>
                                    <h3 className="text-2xl font-bold text-white">审核文档</h3>
                                    <p className="text-sm text-gray-400 mt-1">
                                        {selectedReview.document?.file_name} • AI 置信度: <span className={getConfidenceColor(selectedReview.ai_confidence || 0)}>
                                            {((selectedReview.ai_confidence || 0) * 100).toFixed(0)}%
                                        </span>
                                    </p>
                                </div>
                                <button
                                    onClick={() => setIsReviewModalOpen(false)}
                                    className="text-gray-400 hover:text-white"
                                >
                                    <XCircle size={24} />
                                </button>
                            </div>

                            {/* Editable Fields */}
                            <div className="space-y-4 mb-6">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">提供商</label>
                                        <input
                                            type="text"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={editedData.provider || ''}
                                            onChange={(e) => setEditedData({ ...editedData, provider: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">类型</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={editedData.type || 'Health'}
                                            onChange={(e) => setEditedData({ ...editedData, type: e.target.value })}
                                        >
                                            <option value="Health">Health (健康)</option>
                                            <option value="Auto">Auto (汽车)</option>
                                            <option value="Home">Home (房屋)</option>
                                            <option value="Life">Life (人寿)</option>
                                            <option value="Disability">Disability (伤残)</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">保单号</label>
                                        <input
                                            type="text"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={editedData.policy_number || ''}
                                            onChange={(e) => setEditedData({ ...editedData, policy_number: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">续保日期</label>
                                        <input
                                            type="date"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={editedData.renewal_date || ''}
                                            onChange={(e) => setEditedData({ ...editedData, renewal_date: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">保费</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={editedData.premium || ''}
                                            onChange={(e) => setEditedData({ ...editedData, premium: Number(e.target.value) })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">频率</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={editedData.frequency || 'Monthly'}
                                            onChange={(e) => setEditedData({ ...editedData, frequency: e.target.value })}
                                        >
                                            <option value="Monthly">Monthly (月付)</option>
                                            <option value="Yearly">Yearly (年付)</option>
                                        </select>
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">承保项目</label>
                                    <input
                                        type="text"
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        value={editedData.insured_item || ''}
                                        onChange={(e) => setEditedData({ ...editedData, insured_item: e.target.value })}
                                        placeholder="例如：Family Health Plan, 2023 Toyota RAV4"
                                    />
                                </div>

                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">审核备注（可选）</label>
                                    <textarea
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        rows={3}
                                        value={reviewNotes}
                                        onChange={(e) => setReviewNotes(e.target.value)}
                                        placeholder="添加审核备注..."
                                    />
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-4">
                                <button
                                    onClick={handleApprove}
                                    disabled={actionLoading}
                                    className="flex-1 bg-electric-green hover:bg-green-500 disabled:bg-gray-600 text-black font-bold py-3 rounded-xl flex items-center justify-center gap-2"
                                >
                                    {actionLoading ? (
                                        <Loader2 size={20} className="animate-spin" />
                                    ) : (
                                        <>
                                            <CheckCircle size={20} />
                                            批准并导入
                                        </>
                                    )}
                                </button>
                                <button
                                    onClick={handleReject}
                                    disabled={actionLoading}
                                    className="flex-1 bg-red-500/20 hover:bg-red-500/30 disabled:bg-gray-600 border border-red-500/30 text-red-400 font-bold py-3 rounded-xl flex items-center justify-center gap-2"
                                >
                                    <XCircle size={20} />
                                    拒绝
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Upload Modal */}
            <AnimatePresence>
                {isUploadModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                            onClick={() => setIsUploadModalOpen(false)}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">上传保险文档</h3>
                                <button onClick={() => setIsUploadModalOpen(false)} className="text-gray-400 hover:text-white">
                                    <XCircle size={20} />
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div className="border-2 border-dashed border-grid-border rounded-xl p-8 text-center">
                                    <Upload size={48} className="mx-auto mb-4 text-gray-500" />
                                    <input
                                        type="file"
                                        accept=".pdf,.jpg,.jpeg,.png"
                                        onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                                        className="hidden"
                                        id="file-upload"
                                    />
                                    <label htmlFor="file-upload" className="cursor-pointer">
                                        <div className="text-white font-medium mb-2">
                                            {uploadFile ? uploadFile.name : '点击选择文件'}
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            支持 PDF, JPG, PNG (最大 10MB)
                                        </div>
                                    </label>
                                </div>

                                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                                    <div className="text-sm text-blue-400 font-medium mb-2">AI 自动识别</div>
                                    <div className="text-xs text-gray-400">
                                        系统将自动提取保单信息：提供商、类型、保费、续保日期等，你只需确认即可
                                    </div>
                                </div>

                                <button
                                    onClick={handleUpload}
                                    disabled={!uploadFile || uploading}
                                    className="w-full bg-electric-green hover:bg-green-500 disabled:bg-gray-600 text-black font-bold py-3 rounded-xl"
                                >
                                    {uploading ? (
                                        <Loader2 size={20} className="inline animate-spin mr-2" />
                                    ) : (
                                        <Upload size={20} className="inline mr-2" />
                                    )}
                                    {uploading ? '上传中...' : '开始扫描'}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};
