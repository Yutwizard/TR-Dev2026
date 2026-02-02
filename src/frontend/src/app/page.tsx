'use client';

import Link from 'next/link';
import {
    TrendingUp,
    Building2,
    RefreshCcw,
    Calendar,
    CreditCard,
    BarChart3,
    ShieldCheck,
    Clock,
    ArrowRight,
    ChevronRight,
} from 'lucide-react';

// Quick stats data
const quickStats = [
    {
        label: 'Bond Positions',
        value: '฿ 12.5B',
        change: '+2.3%',
        positive: true,
        icon: TrendingUp
    },
    {
        label: 'Active Interbank',
        value: '฿ 3.2B',
        change: '8 deals',
        positive: true,
        icon: Building2
    },
    {
        label: 'Repo Outstanding',
        value: '฿ 5.8B',
        change: '12 trades',
        positive: true,
        icon: RefreshCcw
    },
    {
        label: 'Pending Settlement',
        value: '15',
        change: 'Due today: 5',
        positive: false,
        icon: Clock
    },
];

// Module cards
const modules = [
    {
        title: 'Bond Trading',
        description: 'Buy/Sell government & corporate bonds with ThaiBMA reporting',
        href: '/bonds',
        icon: TrendingUp,
        color: 'from-blue-500 to-cyan-500',
        features: ['ThaiBMA Integration', 'T+2 Settlement', 'Position Tracking'],
    },
    {
        title: 'Interbank',
        description: 'Money market placements and borrowings with Thai banks',
        href: '/interbank',
        icon: Building2,
        color: 'from-green-500 to-emerald-500',
        features: ['THOR Rate Reference', 'ACT/365 Calculations', 'BAHTNET Settlement'],
    },
    {
        title: 'Repo/Reverse Repo',
        description: 'Secured lending with collateral management and margin calls',
        href: '/repo',
        icon: RefreshCcw,
        color: 'from-purple-500 to-violet-500',
        features: ['Collateral Monitoring', 'Margin Calls', 'Haircut Matrix'],
    },
    {
        title: 'Settlement',
        description: 'BAHTNET cash transfers and TSD securities settlement',
        href: '/settlement',
        icon: CreditCard,
        color: 'from-orange-500 to-amber-500',
        features: ['BAHTNET Messages', 'TSD DVP', 'Status Tracking'],
    },
    {
        title: 'Positions & P&L',
        description: 'Real-time position monitoring and profit/loss analysis',
        href: '/positions',
        icon: BarChart3,
        color: 'from-pink-500 to-rose-500',
        features: ['MTM Valuation', 'TFRS 9 Classification', 'Daily P&L'],
    },
    {
        title: 'Limits & Compliance',
        description: 'Credit limits, utilization tracking, and breach alerts',
        href: '/limits',
        icon: ShieldCheck,
        color: 'from-indigo-500 to-blue-500',
        features: ['Real-time Utilization', 'Breach Alerts', 'Approval Workflow'],
    },
];

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            {/* Header */}
            <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-lg font-bold text-gray-900 dark:text-white">Treasury Management</h1>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Virtual Bank Thailand</p>
                            </div>
                        </div>

                        {/* User info */}
                        <div className="flex items-center gap-4">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-medium text-gray-900 dark:text-white">Admin User</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Front Office</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                <span className="text-primary-600 dark:text-primary-400 font-semibold">AU</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Welcome Section */}
                <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                        Good Morning! 👋
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Today is {new Date().toLocaleDateString('en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                        {' '}&bull;{' '}
                        <span className="text-primary-600 dark:text-primary-400 font-medium">Business Day</span>
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    {quickStats.map((stat) => (
                        <div
                            key={stat.label}
                            className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700 
                         shadow-card hover:shadow-card-hover transition-all duration-200"
                        >
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{stat.label}</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                                    <p className={`text-sm mt-1 ${stat.positive ? 'text-green-600 dark:text-green-400' : 'text-yellow-600 dark:text-yellow-400'}`}>
                                        {stat.change}
                                    </p>
                                </div>
                                <div className="p-3 rounded-lg bg-primary-50 dark:bg-primary-900/30">
                                    <stat.icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Modules Grid */}
                <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Treasury Modules
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {modules.map((module) => (
                            <Link
                                key={module.title}
                                href={module.href}
                                className="group block"
                            >
                                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 
                              shadow-card overflow-hidden transition-all duration-200
                              hover:shadow-card-hover hover:border-primary-300 dark:hover:border-primary-700">
                                    {/* Gradient header */}
                                    <div className={`h-2 bg-gradient-to-r ${module.color}`} />

                                    <div className="p-5">
                                        <div className="flex items-start gap-4">
                                            <div className={`p-3 rounded-xl bg-gradient-to-br ${module.color} flex-shrink-0`}>
                                                <module.icon className="w-6 h-6 text-white" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                                                    {module.title}
                                                </h4>
                                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                                                    {module.description}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Features */}
                                        <div className="mt-4 flex flex-wrap gap-2">
                                            {module.features.map((feature) => (
                                                <span
                                                    key={feature}
                                                    className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium
                                   bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                                                >
                                                    {feature}
                                                </span>
                                            ))}
                                        </div>

                                        {/* Action */}
                                        <div className="mt-4 flex items-center text-sm font-medium text-primary-600 dark:text-primary-400 
                                  group-hover:translate-x-1 transition-transform">
                                            Open Module
                                            <ChevronRight className="w-4 h-4 ml-1" />
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>

                {/* Recent Activity / Pending Items */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Pending Approvals */}
                    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-card">
                        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h4 className="font-semibold text-gray-900 dark:text-white">Pending Approvals</h4>
                        </div>
                        <div className="divide-y divide-gray-100 dark:divide-gray-700">
                            {[
                                { type: 'Bond Trade', ref: 'BT20250201001', amount: '฿ 50.2M', status: 'Pending' },
                                { type: 'Interbank', ref: 'IB20250202001', amount: '฿ 100M', status: 'Pending' },
                                { type: 'Repo', ref: 'RP20250202002', amount: '฿ 80M', status: 'Pending' },
                            ].map((item) => (
                                <div key={item.ref} className="px-5 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                    <div>
                                        <p className="font-medium text-gray-900 dark:text-white">{item.ref}</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">{item.type}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-mono font-medium text-gray-900 dark:text-white">{item.amount}</p>
                                        <span className="badge-warning">{item.status}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-700">
                            <Link href="/approvals" className="text-sm text-primary-600 dark:text-primary-400 font-medium flex items-center hover:underline">
                                View all approvals
                                <ArrowRight className="w-4 h-4 ml-1" />
                            </Link>
                        </div>
                    </div>

                    {/* Today's Settlements */}
                    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-card">
                        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h4 className="font-semibold text-gray-900 dark:text-white">Today's Settlements</h4>
                        </div>
                        <div className="divide-y divide-gray-100 dark:divide-gray-700">
                            {[
                                { type: 'BAHTNET', ref: 'STL001', amount: '฿ 100M', direction: 'OUT', status: 'Pending' },
                                { type: 'TSD DVP', ref: 'STL002', amount: 'LB236A 50M', direction: 'RCV', status: 'Matched' },
                                { type: 'BAHTNET', ref: 'STL003', amount: '฿ 25M', direction: 'IN', status: 'Settled' },
                            ].map((item) => (
                                <div key={item.ref} className="px-5 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                    <div className="flex items-center gap-3">
                                        <span className={`px-2 py-1 text-xs font-medium rounded ${item.direction === 'OUT' ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400' :
                                                item.direction === 'IN' ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400' :
                                                    'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400'
                                            }`}>
                                            {item.direction}
                                        </span>
                                        <div>
                                            <p className="font-medium text-gray-900 dark:text-white">{item.type}</p>
                                            <p className="text-sm text-gray-500 dark:text-gray-400">{item.ref}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-mono font-medium text-gray-900 dark:text-white">{item.amount}</p>
                                        <span className={
                                            item.status === 'Settled' ? 'badge-success' :
                                                item.status === 'Matched' ? 'badge-info' : 'badge-warning'
                                        }>
                                            {item.status}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-700">
                            <Link href="/settlement" className="text-sm text-primary-600 dark:text-primary-400 font-medium flex items-center hover:underline">
                                View all settlements
                                <ArrowRight className="w-4 h-4 ml-1" />
                            </Link>
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="mt-12 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            © 2025 Virtual Bank Thailand. Treasury Management System v0.3.0
                        </p>
                        <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                            <Link href="/calendar" className="flex items-center gap-1 hover:text-primary-600">
                                <Calendar className="w-4 h-4" />
                                Thai Calendar
                            </Link>
                            <span className="text-green-500 flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                System Online
                            </span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
