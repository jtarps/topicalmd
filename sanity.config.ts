import { defineConfig } from "sanity"
import { structureTool } from "sanity/structure"
import { visionTool } from "@sanity/vision"
import { schema } from "./sanity/schema"

export default defineConfig({
  name: "default",
  title: "TopicalMD",

  projectId: "y4u80wnd",
  dataset: "production",

  plugins: [structureTool(), visionTool()],

  schema,

  basePath: "/studio",
})
