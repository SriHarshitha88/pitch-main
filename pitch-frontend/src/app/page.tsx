'use client'

import { motion } from 'framer-motion'
import { MainLayout } from '@/components/layout/main-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Slider } from '@/components/ui/slider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function Home() {
  return (
    <MainLayout>
      {/* Hero Section */}
      <section className="relative py-20">
        <div className="absolute inset-0 -z-10 gradient-mesh" />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="container text-center"
        >
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
            The Future of
            <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
              {" "}Team Collaboration{" "}
            </span>
            is Here
          </h1>
          <p className="mx-auto mt-6 max-w-[700px] text-muted-foreground md:text-xl">
            Pitch is the all-in-one platform for modern teams. Create, collaborate, and share your work with ease.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Button size="lg" variant="premium">
              Get Started
            </Button>
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              Powerful Features for Modern Teams
            </h2>
            <p className="mx-auto mt-4 max-w-[700px] text-muted-foreground">
              Everything you need to create, collaborate, and share your work.
            </p>
          </motion.div>

          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress value={feature.progress} className="h-2" />
                  </CardContent>
                  <CardFooter>
                    <Button variant="ghost" className="w-full">
                      Learn More
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section className="py-20">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              Try It Yourself
            </h2>
            <p className="mx-auto mt-4 max-w-[700px] text-muted-foreground">
              Experience the power of Pitch with our interactive demo.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="mt-16"
          >
            <Tabs defaultValue="demo" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="demo">Interactive Demo</TabsTrigger>
                <TabsTrigger value="features">Features</TabsTrigger>
                <TabsTrigger value="pricing">Pricing</TabsTrigger>
              </TabsList>
              <TabsContent value="demo" className="mt-8">
                <Card>
                  <CardHeader>
                    <CardTitle>Interactive Demo</CardTitle>
                    <CardDescription>
                      Try out our features with this interactive demo.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Adjust Settings</h4>
                      <Slider defaultValue={[50]} max={100} step={1} />
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Progress</h4>
                      <Progress value={75} className="h-2" />
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button variant="premium" className="w-full">
                      Start Demo
                    </Button>
                  </CardFooter>
                </Card>
              </TabsContent>
              <TabsContent value="features">
                <Card>
                  <CardHeader>
                    <CardTitle>Features</CardTitle>
                    <CardDescription>
                      Explore our powerful features.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {features.map((feature) => (
                        <li key={feature.title} className="flex items-center space-x-2">
                          <span className="h-2 w-2 rounded-full bg-primary" />
                          <span>{feature.title}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="pricing">
                <Card>
                  <CardHeader>
                    <CardTitle>Pricing</CardTitle>
                    <CardDescription>
                      Choose the plan that's right for you.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      {pricingPlans.map((plan) => (
                        <Card key={plan.name} className="relative">
                          {plan.popular && (
                            <div className="absolute -top-4 left-0 right-0 mx-auto w-fit rounded-full bg-primary px-4 py-1 text-xs text-primary-foreground">
                              Most Popular
                            </div>
                          )}
                          <CardHeader>
                            <CardTitle>{plan.name}</CardTitle>
                            <CardDescription>{plan.description}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="text-3xl font-bold">${plan.price}</div>
                            <p className="text-sm text-muted-foreground">per month</p>
                          </CardContent>
                          <CardFooter>
                            <Button variant={plan.popular ? "premium" : "outline"} className="w-full">
                              Get Started
                            </Button>
                          </CardFooter>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </motion.div>
        </div>
      </section>
    </MainLayout>
  )
}

const features = [
  {
    title: "Real-time Collaboration",
    description: "Work together with your team in real-time.",
    progress: 90,
  },
  {
    title: "Advanced Analytics",
    description: "Get insights into your team's performance.",
    progress: 75,
  },
  {
    title: "Custom Integrations",
    description: "Connect with your favorite tools and services.",
    progress: 85,
  },
  {
    title: "Secure Storage",
    description: "Your data is safe and secure with us.",
    progress: 95,
  },
  {
    title: "Mobile Access",
    description: "Access your work from anywhere.",
    progress: 80,
  },
  {
    title: "24/7 Support",
    description: "Get help whenever you need it.",
    progress: 100,
  },
]

const pricingPlans = [
  {
    name: "Starter",
    description: "Perfect for small teams",
    price: 9,
    popular: false,
  },
  {
    name: "Pro",
    description: "For growing businesses",
    price: 29,
    popular: true,
  },
  {
    name: "Enterprise",
    description: "For large organizations",
    price: 99,
    popular: false,
  },
] 