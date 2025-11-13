'use client'

import { useState } from 'react'
import DiagramGenerator from '@/components/DiagramGenerator'

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-indigo-900">
          STEM Diagram Generator
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Enter a physics problem description to generate a detailed diagram
        </p>

        <DiagramGenerator />
      </div>
    </main>
  )
}
