import { Outlet, Link } from "react-router-dom"
import { Building2, Search, Settings, Home } from "lucide-react"

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 hidden md:flex">
            <Link to="/" className="mr-6 flex items-center space-x-2">
              <span className="hidden font-bold sm:inline-block">
                AI Atlas
              </span>
            </Link>
            <nav className="flex items-center space-x-6 text-sm font-medium">
              <Link to="/directory" className="transition-colors hover:text-foreground/80 flex items-center gap-2">
                <Home className="h-4 w-4" />
                Directory
              </Link>
              <Link to="/ask-ai" className="transition-colors hover:text-foreground/80 flex items-center gap-2">
                <Search className="h-4 w-4" />
                Ask AI
              </Link>
              <Link to="/admin" className="transition-colors hover:text-foreground/80 flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Admin
              </Link>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="flex-1 container py-6">
        <Outlet />
      </main>
    </div>
  )
}
