import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              SamadhanX
            </h1>
            <p className="text-xl mb-4 opacity-90">
              Jharkhand Societal Innovation Exchange
            </p>
            <p className="text-lg mb-8 opacity-80 max-w-2xl mx-auto">
              Converting real societal problems into university-led innovation projects 
              supported by industry and monitored by government.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                <Link href="/auth/register">Submit a Challenge</Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">How SamadhanX Works</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">👥</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Citizens Submit</h3>
                <p className="text-gray-600">Citizens identify and submit real societal challenges from their communities</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">AI Analysis</h3>
                <p className="text-gray-600">Advanced AI analyzes challenges and matches them with university capabilities</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🎓</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Universities Solve</h3>
                <p className="text-gray-600">Student-faculty teams develop innovative solutions through research projects</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏢</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Industry Supports</h3>
                <p className="text-gray-600">Industry partners provide mentorship, funding, and deployment support</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* User Roles Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Who Can Participate?</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-3 text-blue-600">Citizens</h3>
                <p className="text-gray-600 mb-4">Report challenges, track progress, and see real solutions implemented in your community.</p>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/register?role=citizen">Join as Citizen</Link>
                </Button>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-3 text-green-600">Universities</h3>
                <p className="text-gray-600 mb-4">Connect students and faculty with real-world problems for impactful research projects.</p>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/register?role=university">Join as University</Link>
                </Button>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-3 text-purple-600">Industry</h3>
                <p className="text-gray-600 mb-4">Support meaningful innovation through partnerships, mentorship, and CSR initiatives.</p>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/register?role=industry">Join as Industry</Link>
                </Button>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-3 text-red-600">Government</h3>
                <p className="text-gray-600 mb-4">Monitor progress, validate challenges, and gain insights for policy development.</p>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/register?role=government">Join as Officer</Link>
                </Button>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-3 text-indigo-600">Students & Faculty</h3>
                <p className="text-gray-600 mb-4">Work on real societal challenges while advancing your academic and research goals.</p>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/register?role=academic">Join as Academic</Link>
                </Button>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-xl font-semibold mb-3 text-orange-600">Mentors & Researchers</h3>
                <p className="text-gray-600 mb-4">Guide projects with your expertise and contribute to societal innovation.</p>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/auth/register?role=mentor">Join as Mentor</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Make an Impact?</h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join the SamadhanX community and help solve Jharkhand's most pressing challenges through innovation and collaboration.
          </p>
          <Button asChild size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
            <Link href="/auth/register">Get Started Today</Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">SamadhanX</h3>
              <p className="text-gray-300 mb-4">
                Jharkhand Societal Innovation Exchange - Bridging citizens, universities, and industry for meaningful societal impact.
              </p>
              <p className="text-sm text-gray-400">
                SIH Problem Statement: SIH26043
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="/challenges" className="hover:text-white transition-colors">Browse Challenges</Link></li>
                <li><Link href="/universities" className="hover:text-white transition-colors">Universities</Link></li>
                <li><Link href="/projects" className="hover:text-white transition-colors">Projects</Link></li>
                <li><Link href="/analytics" className="hover:text-white transition-colors">Analytics</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-300">
                <li>Email: info@samadhanx.gov.in</li>
                <li>Phone: +91-XXXX-XXXXXX</li>
                <li>Address: Jharkhand, India</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2026 SamadhanX. Built for SIH 2026 - Jharkhand Societal Innovation Exchange.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}